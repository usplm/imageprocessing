#!/usr/bin/env python
# coding: utf-8
"""
Test panel class

Copyright 2017 MicaSense, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os, glob
import math
import micasense.image as image
import micasense.panel as panel

def test_qr_corners(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    qr_corners = pan.qr_corners()
    good_qr_corners = [[460, 599], [583, 599], [584, 478], [462, 477]]
    assert qr_corners is not None
    assert len(qr_corners) == len(good_qr_corners)
    assert pan.serial == 'RP02-1603036-SC'
    for i, pt in enumerate(qr_corners):
        # different opencv/zbar versions round differently it seems
        assert pt[0] == pytest.approx(good_qr_corners[i][0], abs=3)
        assert pt[1] == pytest.approx(good_qr_corners[i][1], abs=3)

def test_panel_corners(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    panel_pts = pan.panel_corners()
    good_pts = [[809, 613], [648, 615], [646, 454], [808, 452]]
    assert panel_pts is not None
    assert len(panel_pts) == len(good_pts)
    assert pan.serial == 'RP02-1603036-SC'
    for i, pt in enumerate(panel_pts):
        # different opencv/zbar versions round differently it seems
        assert pt[0] == pytest.approx(good_pts[i][0], abs=3)
        assert pt[1] == pytest.approx(good_pts[i][1], abs=3)

# test manually providing bad corners - in this case the corners of the qr code itself
def test_raw_panel_bad_corners(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img,panelCorners=[[460, 599], [583, 599], [584, 478], [462, 477]])
    mean, std, num, sat = pan.raw()
    assert mean == pytest.approx(26965, rel=0.01)
    assert std == pytest.approx(15396.0, rel=0.05)
    assert num == pytest.approx(14824, rel=0.01)
    assert sat == pytest.approx(0, abs=2)

# test manually providing good corners
def test_raw_panel_manual(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img,panelCorners=[[809, 613], [648, 615], [646, 454], [808, 452]])
    mean, std, num, sat = pan.raw()
    assert mean == pytest.approx(45406, rel=0.01)
    assert std == pytest.approx(738.0, rel=0.05)
    assert num == pytest.approx(26005, rel=0.001)
    assert sat == pytest.approx(0, abs=2)

def test_raw_panel(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    mean, std, num, sat = pan.raw()
    assert mean == pytest.approx(45406.0, rel=0.01)
    assert std == pytest.approx(738.0, rel=0.05)
    assert num == pytest.approx(26005, rel=0.02)
    assert sat == pytest.approx(0, abs=2)

def test_intensity_panel(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    mean, std, num, sat = pan.intensity()
    assert mean == pytest.approx(1162, rel=0.01)
    assert std == pytest.approx(23, rel=0.03)
    assert num == pytest.approx(26005, rel=0.02)
    assert sat == pytest.approx(0, abs=2)

def test_radiance_panel(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    mean, std, num, sat = pan.radiance()
    assert mean == pytest.approx(0.170284, rel=0.01)
    assert std == pytest.approx(0.0033872969661854742, rel=0.02)
    assert num == pytest.approx(26005, rel=0.02)
    assert sat == pytest.approx(0, abs=2)

def test_irradiance_mean(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    panel_reflectance = 0.67
    mean = pan.irradiance_mean(panel_reflectance)
    assert mean == pytest.approx(0.7984, rel=0.001)
    
def test_panel_detected(panel_image_name):
    img = image.Image(panel_image_name)
    pan = panel.Panel(img)
    assert pan.panel_detected() == True

def test_panel_not_detected(flight_image_name):
    img = image.Image(flight_image_name)
    pan = panel.Panel(img)
    assert pan.panel_detected() == False

def test_altum_panel(altum_panel_image_name):
    img = image.Image(altum_panel_image_name)
    assert img.auto_calibration_image == True
    pan = panel.Panel(img)
    panel_pts = pan.panel_corners()
    good_pts = [[1278, 483], [1176, 491], [1184, 591], [1286, 583]]
    assert panel_pts is not None
    assert len(panel_pts) == len(good_pts)
    assert pan.serial == 'RP04-1901231-SC'
    print(panel_pts)
    for i, pt in enumerate(panel_pts):
        # different opencv/zbar versions round differently it seems
        assert pt[0] == pytest.approx(good_pts[i][0], abs=3)
        assert pt[1] == pytest.approx(good_pts[i][1], abs=3)
    assert pan.qr_corners() == None

def test_altum_lwir(altum_lwir_image_name):
    img = image.Image(altum_lwir_image_name)
    assert img.auto_calibration_image == False
    pan = panel.Panel(img)
    assert pan.panel_detected() == False


def test_ordered_coordinates(panel_image_name):
    img = image.Image(panel_image_name)
    if img.panel_region is not None:
        ordered_corners = img.panel_region
    else:
        ordered_corners = [(809, 613), (648, 615), (646, 454), (808, 452)]
    pan = panel.Panel(img, panelCorners=ordered_corners)
    assert pan.ordered_panel_coordinates() == ordered_corners


def test_unordered_coordinates(panel_image_name):
    img = image.Image(panel_image_name)
    ordered_corners = [(809, 613), (648, 615), (646, 454), (808, 452)]
    unordered_corners = [(648, 615), (809, 613), (808, 452), (646, 454)]
    pan = panel.Panel(img, panelCorners=unordered_corners)
    assert pan.ordered_panel_coordinates() == ordered_corners