#!/usr/bin/env python

from __future__ import division, print_function

import os
import argparse
import subprocess
import cv2
import jinja2
import numpy as np
from skimage import img_as_ubyte
from pdf2image import convert_from_path
from latex import tokenize, extract_equations



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('texfile')
    parser.add_argument('--template', default='misc/template.tex')
    args = parser.parse_args()
    return args



def render_tex(filename, outdir='output'):
    """render latex document"""
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    command = ['latexmk', '-outdir=' + outdir, '-pdf', basename]
    returncode = subprocess.call(command, cwd=dirname)
    pdf_name = os.path.join(dirname, outdir, os.path.splitext(basename)[0] + '.pdf')
    return pdf_name



def render_equation(equation, template, filename):
    tex = ''.join(repr(c) for c in equation)
    equation_tex = template.render(equation=tex)
    with open(filename, 'w') as f:
        f.write(equation_tex)
    pdf_name = render_tex(filename)
    image = get_pages(pdf_name)[0]
    return image



def get_pages(pdf_name):
    pages = []
    for img in convert_from_path(pdf_name):
        page = np.array(img)
        page = cv2.cvtColor(page, cv2.COLOR_RGB2GRAY)
        pages.append(page)
    return pages



def match_template(pages, template):
    best_max_val = -np.inf
    best_max_loc = (-1, -1)
    best_page = -1
    for i, page in enumerate(pages):
        result = cv2.matchTemplate(page, template, cv2.TM_CCOEFF_NORMED)
        (_, max_val, _, max_loc) = cv2.minMaxLoc(result)
        if best_max_val < max_val:
            best_max_val = max_val
            best_max_loc = max_loc
            best_page = i
    upper_left = best_max_loc
    lower_right = (best_max_loc[0] + template.shape[1], best_max_loc[1] + template.shape[0])
    return best_max_val, best_page, upper_left, lower_right



if __name__ == '__main__':
    args = parse_args()
    tokens = tokenize(args.texfile)
    equations = extract_equations(tokens)
    pdf_name = render_tex(args.texfile)
    pages = get_pages(pdf_name)
    template_loader = jinja2.FileSystemLoader(searchpath='.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(args.template)
    for j, eq_tex in enumerate(equations):
        equation = render_equation(eq_tex, template, 'examples/equation.tex')
        cv2.imwrite('template.jpeg', equation)
        match, i, start, end = match_template(pages, equation)
        print('=' * 70)
        print(eq_tex)
        print('=' * 70)
        image = pages[i].copy()
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(image, start, end, (0, 0, 255), 2)
        cv2.imwrite('eq%s.jpeg' % j, image)
