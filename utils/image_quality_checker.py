"""
Image Quality Checker - Detects blur, lighting issues, and image quality
"""

import cv2
import numpy as np
from pathlib import Path

class ImageQualityChecker:
    def __init__(self):
        # Thresholds for quality checks
        self.BLUR_THRESHOLD = 50.0  # Lower = more blurred
        self.MIN_BRIGHTNESS = 40
        self.MAX_BRIGHTNESS = 220
        self.MIN_FACES = 1
        
    def calculate_blur_score(self, image_path):
        """
        Calculate blur score using Laplacian variance
        Higher score = sharper image
        Lower score = more blurred
        """
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return {'valid': False, 'error': 'Could not read image'}
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (blur metric)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return {
                'valid': True,
                'blur_score': float(laplacian_var),
                'is_blurred': laplacian_var < self.BLUR_THRESHOLD
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def check_brightness(self, image_path):
        """Check if image has adequate lighting"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return {'valid': False, 'error': 'Could not read image'}
            
            # Convert to grayscale and calculate mean brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)
            
            is_too_dark = mean_brightness < self.MIN_BRIGHTNESS
            is_too_bright = mean_brightness > self.MAX_BRIGHTNESS
            
            return {
                'valid': True,
                'brightness': float(mean_brightness),
                'is_too_dark': is_too_dark,
                'is_too_bright': is_too_bright,
                'is_adequate': not (is_too_dark or is_too_bright)
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def check_resolution(self, image_path):
        """Check if image resolution is adequate"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return {'valid': False, 'error': 'Could not read image'}
            
            height, width = image.shape[:2]
            
            # Minimum recommended resolution
            min_width = 640
            min_height = 480
            
            return {
                'valid': True,
                'width': width,
                'height': height,
                'is_adequate': width >= min_width and height >= min_height
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def comprehensive_check(self, image_path):
        """
        Perform comprehensive quality check on image
        Returns detailed report with recommendations
        """
        results = {
            'image_path': str(image_path),
            'is_acceptable': True,
            'issues': [],
            'warnings': [],
            'details': {}
        }
        
        # Check blur
        blur_result = self.calculate_blur_score(image_path)
        results['details']['blur'] = blur_result
        
        if blur_result.get('valid'):
            if blur_result.get('is_blurred'):
                results['is_acceptable'] = False
                results['issues'].append({
                    'type': 'blur',
                    'severity': 'critical',
                    'message': f"Image is too blurred (score: {blur_result['blur_score']:.2f}). Please upload a clearer image.",
                    'recommendation': 'Hold camera steady and ensure proper focus'
                })
        
        # Check brightness
        brightness_result = self.check_brightness(image_path)
        results['details']['brightness'] = brightness_result
        
        if brightness_result.get('valid'):
            if brightness_result.get('is_too_dark'):
                results['is_acceptable'] = False
                results['issues'].append({
                    'type': 'lighting',
                    'severity': 'critical',
                    'message': 'Image is too dark. Please improve lighting.',
                    'recommendation': 'Turn on lights or move to a brighter location'
                })
            elif brightness_result.get('is_too_bright'):
                results['warnings'].append({
                    'type': 'lighting',
                    'severity': 'warning',
                    'message': 'Image may be overexposed.',
                    'recommendation': 'Avoid direct sunlight or reduce exposure'
                })
        
        # Check resolution
        resolution_result = self.check_resolution(image_path)
        results['details']['resolution'] = resolution_result
        
        if resolution_result.get('valid'):
            if not resolution_result.get('is_adequate'):
                results['warnings'].append({
                    'type': 'resolution',
                    'severity': 'warning',
                    'message': f"Low resolution ({resolution_result['width']}x{resolution_result['height']})",
                    'recommendation': 'Use a higher resolution camera if possible'
                })
        
        # Generate quality score (0-100)
        quality_score = 100
        if blur_result.get('valid') and blur_result.get('is_blurred'):
            quality_score -= 50
        if brightness_result.get('valid'):
            if brightness_result.get('is_too_dark') or brightness_result.get('is_too_bright'):
                quality_score -= 30
        if resolution_result.get('valid') and not resolution_result.get('is_adequate'):
            quality_score -= 20
        
        results['quality_score'] = max(0, quality_score)
        
        return results
    
    def batch_check(self, image_paths):
        """Check multiple images at once"""
        results = []
        for image_path in image_paths:
            result = self.comprehensive_check(image_path)
            results.append(result)
        
        return {
            'total_images': len(results),
            'acceptable_count': sum(1 for r in results if r['is_acceptable']),
            'rejected_count': sum(1 for r in results if not r['is_acceptable']),
            'results': results
        }