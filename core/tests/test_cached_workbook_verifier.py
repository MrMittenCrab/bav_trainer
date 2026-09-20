"""Saved-cache acceptance must fail on errors, changed formulas and wrong values."""
import json
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest
from openpyxl import Workbook

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/verify_cached_workbook.py'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def fixture(tmp_path, failure):
    original = tmp_path / 'arbitrary-original.xlsx'
    copy = tmp_path / 'arbitrary-copy.xlsx'
    wb = Workbook(); wb.active.title = 'Analysis'
    wb.active['A1'] = "=Hidden!A1*2"
    hidden = wb.create_sheet('Hidden'); hidden.sheet_state = 'hidden'
    hidden['A1'] = '=20+1'
    wb.save(original); wb.close()
    with ZipFile(original) as src, ZipFile(copy, 'w') as dst:
        for name in src.namelist():
            data = src.read(name)
            if name in ('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet2.xml'):
                xml = ET.fromstring(data)
                cell = xml.find('.//' + NS + 'c')
                value = 42 if 'sheet1' in name else 21
                if 'sheet2' in name:
                    if failure == 'formula': cell.find(NS+'f').text = '19+2'
                    if failure == 'missing': value = None
                    if failure == 'error': cell.set('t', 'e'); value = '#VALUE!'
                if failure == 'mismatch' and 'sheet1' in name: value = 43
                cell.find(NS+'v').text = None if value is None else str(value)
                data = ET.tostring(xml)
            dst.writestr(name, data)
    refs = tmp_path / 'references.json'
    refs.write_text(json.dumps({'sheets': ['Analysis'], 'cells': [
        {'sheet': 'Analysis', 'cell': 'A1', 'value': 42, 'source': 'Independent arithmetic: (20+1)*2'}]}))
    return original, copy, refs


@pytest.mark.parametrize('failure,reason', [('', ''), ('formula', 'formula'),
    ('missing', 'cache'), ('error', 'cache'), ('mismatch', 'reference')])
def test_saved_copy_acceptance(tmp_path, failure, reason):
    original, copy, refs = fixture(tmp_path, failure)
    before = [p.read_bytes() for p in (original, copy, refs)]
    result = subprocess.run([sys.executable, str(SCRIPT), str(copy), '--original',
        str(original), '--references', str(refs)], capture_output=True, text=True)
    assert result.returncode == (1 if failure else 0), result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report['status'] == ('BLOCKED' if failure else 'VERIFIED')
    if failure: assert reason in report['action'].lower()
    else: assert report['checked_cells'] == 2
    assert before == [p.read_bytes() for p in (original, copy, refs)]


def test_empty_references_cannot_pass(tmp_path):
    original, copy, refs = fixture(tmp_path, '')
    refs.write_text('{"sheets": ["Analysis"], "cells": []}')
    result = subprocess.run([sys.executable, str(SCRIPT), str(copy), '--original',
        str(original), '--references', str(refs)], capture_output=True, text=True)
    assert result.returncode == 1
    assert 'reference' in json.loads(result.stdout)['action'].lower()
