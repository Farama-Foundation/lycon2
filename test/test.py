import cv2
import lycon2

import hashlib
import numpy as np
import os
import shutil
import tempfile
import unittest

def random_rgb_image():
    return (255*np.random.rand(128, 42, 3)).astype(np.uint8)

def rgb_bgr(img):
    return img[:, :, (2, 1, 0)]

def filehash(path):
    buffer_size = 65536
    md5 = hashlib.md5()
    with open(path, 'rb') as infile:
        while True:
            data = infile.read(buffer_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

class TestAgainstOpenCV(unittest.TestCase):

    def setUp(self):
        self.temp_path = tempfile.mkdtemp(prefix='lycon2_test_')

    def tearDown(self):
        shutil.rmtree(self.temp_path)

    def get_path(self, filename):
        return os.path.join(self.temp_path, filename)

    def test_save(self):
        img = random_rgb_image()
        for extension in lycon2.get_supported_extensions():
            mkpath = lambda name : self.get_path('{}.{}'.format(name, extension))
            # Write using Lycon2
            lycon2.save(mkpath('opencv'), img)
            # Write using OpenCV
            cv2.imwrite(mkpath('lycon2'), rgb_bgr(img))
            self.assertEqual(filehash(mkpath('opencv')), filehash(mkpath('lycon2')))

    def test_load(self):
        img = random_rgb_image()
        for extension in lycon2.get_supported_extensions():
            mkpath = lambda name : self.get_path('{}.{}'.format(name, extension))
            # Write using OpenCV
            cv2.imwrite(mkpath('opencv'), img)
            # Read using OpenCV
            cv_img = cv2.imread(mkpath('opencv'))
            # Read using Lycon2
            lycon2_img = rgb_bgr(lycon2.load(mkpath('opencv')))
            np.testing.assert_array_equal(cv_img, lycon2_img)

    def test_no_nan(self):
        src_img = random_rgb_image()
        images = [src_img,
                  src_img.astype(np.float32),
                  src_img.astype(np.float64),
                  src_img.astype(np.int16)]                  
        new_shapes = [
            # No change
            src_img.shape[:2],
            # Upsample 2x
            tuple(map(int, np.array(src_img.shape[:2]) * 2)),
            # Upsample 3x
            tuple(map(int, np.array(src_img.shape[:2]) * 3)),
            # Downsample
            tuple(map(int, np.array(src_img.shape[:2]) // 2))
        ]
        for img in images:
            for (h, w) in new_shapes:
                for interp in range(4):
                    cv_resized = cv2.resize(img, (w, h), interpolation=interp)
                    lycon2_resized = lycon2.resize(img, width=w, height=h, interpolation=interp)
                    self.assertTrue(not np.isnan(np.sum(cv_resized)),
                            'NaN with OpenCV for dtype={}, interp={}, size=({}, {})'.format(
                                img.dtype, interp, w, h))
                    self.assertTrue(not np.isnan(np.sum(lycon2_resized)),
                            'NaN with lycon2 for dtype={}, interp={}, size=({}, {})'.format(
                                img.dtype, interp, w, h))

    def test_resize(self):
        #TODO: OpenCV results depend on version. Need a fixed baseline, or?
        if True:
            return
        src_img = random_rgb_image()
        images = [
                  src_img.astype(np.float32),
                  src_img.astype(np.float64),
                  src_img.astype(np.int16)]                  
        new_shapes = [
            # No change
            src_img.shape[:2],
            # Upsample 2x
            tuple(map(int, np.array(src_img.shape[:2]) * 2)),
            # Upsample 3x
            tuple(map(int, np.array(src_img.shape[:2]) * 3)),
            # Downsample
            tuple(map(int, np.array(src_img.shape[:2]) // 2))
        ]
        for img in images:
            for (h, w) in new_shapes:
                for interp in range(4):
                    cv_resized = cv2.resize(img, (w, h), interpolation=interp)
                    lycon2_resized = lycon2.resize(img, width=w, height=h, interpolation=interp)
                    np.testing.assert_allclose(
                        cv_resized,
                        lycon2_resized,
                        err_msg='Mismatch for dtype={}, interp={}, size=({}, {})'.format(
                            img.dtype, interp, w, h
                        ),
                        rtol=1e-5,
                        atol=1e-3
                    )


if __name__ == '__main__':
    unittest.main()
