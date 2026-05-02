# Sign-to-Text Camera Orientation & Left-Hand Support Updates

## Summary
This document outlines the changes made to fix camera orientation issues and add left-hand support to the Sign Language Recognition system.

## Issues Fixed

### 1. Camera Orientation Mismatch
**Problem:** The camera preview was mirrored differently than the skeleton overlay, causing confusion.

**Solution:** 
- Removed the `cv2.flip(frame, 1)` call in the backend that was causing double-flipping
- Added CSS transform `scaleX(-1)` to the video element for natural mirrored camera view
- Both camera preview and skeleton overlay now show the same orientation

### 2. Left-Hand Support
**Problem:** The system only recognized right-hand gestures correctly.

**Solution:**
- Updated Mediapipe detection to identify both left and right hands
- Added logic to prioritize right hand when both hands are visible
- Implemented coordinate mirroring for left-hand landmarks before prediction
- Left-hand coordinates are flipped horizontally to match the right-hand training data

## Files Modified

### 1. `app.py` - Backend Changes

#### `/predict` Route Updates (Lines 536-654)

**Removed double-flip:**
```python
# OLD CODE (removed):
frame = cv2.flip(frame, 1)

# NEW CODE:
# Don't flip frame - let Mediapipe handle it with flipType=True
# This ensures camera preview and skeleton display match orientation
```

**Added hand detection and selection logic:**
```python
# Select hand based on priority: right hand first, then left
hand = None
hand_type = 'Right'
for h in hands:
    hand_info = h[0]
    if hand_info.get('type') == 'Right':
        hand = h
        hand_type = 'Right'
        break
if hand is None:
    hand = hands[0]
    hand_type = hand[0].get('type', 'Right')
```

**Added left-hand coordinate mirroring:**
```python
# Mirror x-coordinates for left hand to match right hand training data
if hand_type == 'Left':
    crop_width = image_crop.shape[1]
    pts = [[crop_width - pt[0], pt[1], pt[2]] for pt in pts]
```

**Updated response to include hand type:**
```python
return jsonify({
    'success': True,
    'current_symbol': current_symbol,
    'sentence': str_text,
    'suggestions': [word1, word2, word3, word4],
    'processed_image': processed_image,
    'hand_type': hand_type  # NEW
})
```

### 2. `templates/index.html` - Frontend Changes

#### CSS Updates (Lines 171-209)

**Added video mirroring:**
```css
/* Mirror video for natural camera view */
.video-container video {
    transform: scaleX(-1);
    width: 100%;
    height: 100%;
    object-fit: cover;
}
```

**Added hand detection indicator styling:**
```css
/* Hand detection indicator */
.hand-indicator {
    background: rgba(102, 126, 234, 0.1);
    border: 2px solid rgba(102, 126, 234, 0.3);
    border-radius: 10px;
    padding: 8px 16px;
    text-align: center;
    font-size: 0.9em;
    color: #667eea;
    font-weight: 600;
    margin-bottom: 12px;
}

.hand-indicator.left-hand {
    background: rgba(118, 75, 162, 0.1);
    border-color: rgba(118, 75, 162, 0.3);
    color: #764ba2;
}

.no-hand-message {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 107, 107, 0.9);
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.9em;
    font-weight: 600;
}
```

#### HTML Updates (Lines 414-416)

**Added hand detection indicator UI:**
```html
<div class="panel prediction-container">
    <div id="handIndicator" class="hand-indicator" style="display: none;">
        Detecting: <span id="handType">Auto</span>
    </div>
    <!-- Rest of prediction container -->
</div>
```

#### JavaScript Updates

**Added hand indicator element references (Lines 461-462):**
```javascript
this.handIndicator = document.getElementById('handIndicator');
this.handType = document.getElementById('handType');
```

**Updated display logic to show hand type (Lines 617-638):**
```javascript
updateDisplay(result) {
    this.characterDisplay.textContent = result.current_symbol || 'C';
    this.sentenceDisplay.textContent = result.sentence || ' ';
    
    // Update hand type indicator
    if (result.hand_type) {
        this.handIndicator.style.display = 'block';
        this.handType.textContent = result.hand_type + ' Hand';
        if (result.hand_type === 'Left') {
            this.handIndicator.classList.add('left-hand');
        } else {
            this.handIndicator.classList.remove('left-hand');
        }
    }
    
    if (result.processed_image) {
        this.processedImage.src = 'data:image/jpeg;base64,' + result.processed_image;
        this.processedImage.style.display = 'block';
        this.skeletonPlaceholder.style.display = 'none';
        this.noHandMessage.style.display = 'none';
    } else {
        this.processedImage.style.display = 'none';
        this.skeletonPlaceholder.style.display = 'none';
        this.noHandMessage.style.display = 'block';
        this.handIndicator.style.display = 'none';
    }
    
    // Update suggestions...
}
```

## How It Works

### Camera Orientation Flow:
1. Browser captures video from webcam (natural view)
2. Frontend applies CSS `scaleX(-1)` to mirror video for user (like looking in a mirror)
3. Backend receives frame and processes with `flipType=True` in Mediapipe
4. Both displays show the same mirrored orientation

### Left-Hand Detection Flow:
1. Mediapipe detects all hands and identifies their type (Left/Right)
2. Backend prioritizes right hand if both are visible
3. For left-hand detection:
   - Extracts hand landmarks
   - Mirrors x-coordinates: `new_x = crop_width - old_x`
   - Feeds mirrored coordinates to the prediction model
4. Model processes mirrored left-hand coordinates as if they were right-hand
5. Frontend displays which hand is being detected

### Hand Priority Logic:
- **Both hands visible:** Uses right hand
- **Only right hand:** Uses right hand
- **Only left hand:** Uses left hand (with coordinate mirroring)

## Visual Indicators

- **Right Hand Detection:** Blue indicator showing "Detecting: Right Hand"
- **Left Hand Detection:** Purple indicator showing "Detecting: Left Hand"
- **No Hand:** Red message at bottom of skeleton panel

## Testing Recommendations

1. **Camera Orientation Test:**
   - Hold up your right hand
   - Verify camera preview and skeleton overlay both show hand on the same side
   - No left-right flip mismatch should occur

2. **Left-Hand Recognition Test:**
   - Show only left hand to camera
   - Verify "Detecting: Left Hand" appears in purple
   - Make gestures (A, B, C, etc.) with left hand
   - Verify recognition works correctly

3. **Right-Hand Recognition Test:**
   - Show only right hand to camera
   - Verify "Detecting: Right Hand" appears in blue
   - Make gestures and verify recognition

4. **Both Hands Test:**
   - Show both hands to camera
   - System should prioritize right hand
   - Indicator should show "Right Hand"

## Known Limitations

1. When both hands are visible, only the right hand is used for recognition
2. The model was trained on right-hand data, so left-hand gestures are mirrored to match
3. Some complex gestures might have slight accuracy differences between left and right hands

## Future Improvements

- Add dual-hand mode for simultaneous recognition
- Train separate models for left and right hands
- Add hand-switching toggle in UI
- Show confidence scores for predictions
