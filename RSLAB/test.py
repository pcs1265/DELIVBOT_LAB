from enum import IntEnum
import pyrealsense2 as rs
import dlib
import numpy as np

class markup_68(IntEnum):
    # Starting with right ear, the jaw [1-17]
    RIGHT_EAR = 0,
    JAW_FROM = 0,
    RIGHT_JAW_FROM = 0,
    RIGHT_1 = 1,
    RIGHT_2 = 2,
    RIGHT_3 = 3, 
    RIGHT_4 = 4, 
    RIGHT_5 = 5, 
    RIGHT_6 = 6, 
    RIGHT_7 = 7,
    RIGHT_JAW_TO = 7,
    CHIN = 8,
    CHIN_FROM = 7,
    CHIN_TO = 9,
    LEFT_7 = 9,
    LEFT_JAW_FROM = 9,
    LEFT_6 = 10,
    LEFT_5 = 11,
    LEFT_4 = 12,
    LEFT_3 = 13,
    LEFT_2 = 14,
    LEFT_1 = 15,
    LEFT_EAR = 16,
    LEFT_JAW_TO = 16,
    JAW_TO = 16,

    # Eyebrows [18-22] and [23-27]
    RIGHT_EYEBROW_R = 17,
    RIGHT_EYEBROW_FROM = 17,
    RIGHT_EYEBROW_1 = 18,
    RIGHT_EYEBROW_2 = 19,
    RIGHT_EYEBROW_3 = 20,
    RIGHT_EYEBROW_L = 21,
    RIGHT_EYEBROW_TO = 21,
    LEFT_EYEBROW_R = 22,
    LEFT_EYEBROW_FROM = 22,
    LEFT_EYEBROW_1 = 23,
    LEFT_EYEBROW_2 = 24,
    LEFT_EYEBROW_3 = 25,
    LEFT_EYEBROW_L = 26,
    LEFT_EYEBROW_TO = 26,

    # Nose [28-36]
    NOSE_RIDGE_TOP = 27,
    NOSE_RIDGE_FROM = 27,
    NOSE_RIDGE_1 = 28,
    NOSE_RIDGE_2 = 29,
    NOSE_TIP = 30,
    NOSE_RIDGE_TO = 30,
    NOSE_BOTTOM_R = 31,
    NOSE_BOTTOM_FROM = 31,
    NOSE_BOTTOM_1 = 32,
    NOSE_BOTTOM_2 = 33,
    NOSE_BOTTOM_3 = 34,
    NOSE_BOTTOM_L = 35,
    NOSE_BOTTOM_TO = 35,

    # Eyes [37-42] and [43-48]
    RIGHT_EYE_R = 36,
    RIGHT_EYE_FROM = 36,
    RIGHT_EYE_1 = 37,
    RIGHT_EYE_2 = 38,
    RIGHT_EYE_L = 39,
    RIGHT_EYE_4 = 40,
    RIGHT_EYE_5 = 41,
    RIGHT_EYE_TO = 41,
    LEFT_EYE_R = 42,
    LEFT_EYE_FROM = 42,
    LEFT_EYE_1 = 43,
    LEFT_EYE_2 = 44,
    LEFT_EYE_L = 45,
    LEFT_EYE_4 = 46,
    LEFT_EYE_5 = 47,
    LEFT_EYE_TO = 47,

    # Mouth [49-68]
    MOUTH_R = 48,
    MOUTH_OUTER_R = 48,
    MOUTH_OUTER_FROM = 48,
    MOUTH_OUTER_1 = 49,
    MOUTH_OUTER_2 = 50,
    MOUTH_OUTER_TOP = 51,
    MOUTH_OUTER_4 = 52,
    MOUTH_OUTER_5 = 53,
    MOUTH_L = 54,
    MOUTH_OUTER_L = 54,
    MOUTH_OUTER_7 = 55,
    MOUTH_OUTER_8 = 56,
    MOUTH_OUTER_BOTTOM = 57,
    MOUTH_OUTER_10 = 58,
    MOUTH_OUTER_11 = 59,
    MOUTH_OUTER_TO = 59,
    MOUTH_INNER_R = 60,
    MOUTH_INNER_FROM = 60,
    MOUTH_INNER_1 = 61,
    MOUTH_INNER_TOP = 62,
    MOUTH_INNER_3 = 63,
    MOUTH_INNER_L = 64,
    MOUTH_INNER_5 = 65,
    MOUTH_INNER_BOTTOM = 66,
    MOUTH_INNER_7 = 67,
    MOUTH_INNER_TO = 67,

    N_POINTS = 68
    

# class markup_68(Enum):
#     # Starting with right ear, the jaw [1-17]
#     RIGHT_EAR, JAW_FROM = 1,
#     RIGHT_JAW_FROM = RIGHT_EAR,
#     RIGHT_1 = 2,
#     RIGHT_2 = 3,
#     RIGHT_3 = 4, 
#     RIGHT_4 = 5, 
#     RIGHT_5 = 6, 
#     RIGHT_6 = 7, 
#     RIGHT_7 = 8,
#     RIGHT_JAW_TO = RIGHT_7,
#     CHIN = 9,
#     CHIN_FROM = CHIN - 1, #8
#     CHIN_TO = CHIN + 1, #10
#     LEFT_7 = CHIN + 1, #10
#     LEFT_JAW_FROM = LEFT_7,
#     LEFT_6 = 11,
#     LEFT_5 = 12,
#     LEFT_4 = 13,
#     LEFT_3 = 14,
#     LEFT_2 = 15,
#     LEFT_1 = 16,
#     LEFT_EAR = 17,
#     LEFT_JAW_TO = LEFT_EAR,
#     JAW_TO = LEFT_EAR,

#     # Eyebrows [18-22] and [23-27]
#     RIGHT_EYEBROW_R = 18,
#     RIGHT_EYEBROW_FROM = RIGHT_EYEBROW_R,
#     RIGHT_EYEBROW_1 = 19,
#     RIGHT_EYEBROW_2 = 20,
#     RIGHT_EYEBROW_3 = 21,
#     RIGHT_EYEBROW_L = 22,
#     RIGHT_EYEBROW_TO = RIGHT_EYEBROW_L,
#     LEFT_EYEBROW_R = 23,
#     LEFT_EYEBROW_FROM = LEFT_EYEBROW_R,
#     LEFT_EYEBROW_1 = 24,
#     LEFT_EYEBROW_2 = 25,
#     LEFT_EYEBROW_3 = 26,
#     LEFT_EYEBROW_L = 27,
#     LEFT_EYEBROW_TO = LEFT_EYEBROW_L,

#     # Nose [28-36]
#     NOSE_RIDGE_TOP = 28,
#     NOSE_RIDGE_FROM = NOSE_RIDGE_TOP,
#     NOSE_RIDGE_1 = 29,
#     NOSE_RIDGE_2 = 30,
#     NOSE_TIP = 31,
#     NOSE_RIDGE_TO = NOSE_TIP,
#     NOSE_BOTTOM_R = 32,
#     NOSE_BOTTOM_FROM = NOSE_BOTTOM_R,
#     NOSE_BOTTOM_1 = 33,
#     NOSE_BOTTOM_2 = 34,
#     NOSE_BOTTOM_3 = 35,
#     NOSE_BOTTOM_L = 36,
#     NOSE_BOTTOM_TO = NOSE_BOTTOM_L,

#     # Eyes [37-42] and [43-48]
#     RIGHT_EYE_R = 37,
#     RIGHT_EYE_FROM = RIGHT_EYE_R,
#     RIGHT_EYE_1 = 38,
#     RIGHT_EYE_2 = 39,
#     RIGHT_EYE_L = 40,
#     RIGHT_EYE_4 = 41,
#     RIGHT_EYE_5 = 42,
#     RIGHT_EYE_TO = RIGHT_EYE_5,
#     LEFT_EYE_R = 43,
#     LEFT_EYE_FROM = LEFT_EYE_R,
#     LEFT_EYE_1 = 44,
#     LEFT_EYE_2 = 45,
#     LEFT_EYE_L = 46,
#     LEFT_EYE_4 = 47,
#     LEFT_EYE_5 = 48,
#     LEFT_EYE_TO = LEFT_EYE_5,

#     # Mouth [49-68]
#     MOUTH_R = 49,
#     MOUTH_OUTER_R = MOUTH_R,
#     MOUTH_OUTER_FROM = MOUTH_OUTER_R,
#     MOUTH_OUTER_1 = 50,
#     MOUTH_OUTER_2 = 51,
#     MOUTH_OUTER_TOP = 52,
#     MOUTH_OUTER_4 = 53,
#     MOUTH_OUTER_5 = 54,
#     MOUTH_L = 55,
#     MOUTH_OUTER_L = MOUTH_L,
#     MOUTH_OUTER_7 = 56,
#     MOUTH_OUTER_8 = 57,
#     MOUTH_OUTER_BOTTOM = 58,
#     MOUTH_OUTER_10 = 59,
#     MOUTH_OUTER_11 = 60,
#     MOUTH_OUTER_TO = MOUTH_OUTER_11,
#     MOUTH_INNER_R = 61,
#     MOUTH_INNER_FROM = MOUTH_INNER_R,
#     MOUTH_INNER_1 = 62,
#     MOUTH_INNER_TOP = 63,
#     MOUTH_INNER_3 = 64,
#     MOUTH_INNER_L = 65,
#     MOUTH_INNER_5 = 66,
#     MOUTH_INNER_BOTTOM = 67,
#     MOUTH_INNER_7 = 68,
#     MOUTH_INNER_TO = MOUTH_INNER_7,

#     N_POINTS = 

# Calculates the average depth for a range of two-dimentional points in face, such that:
#     point(n) = face.part(n)
# and puts the result in *p_average_depth.
# Points for which no depth is available (is 0) are ignored and not factored into the average.
# Returns true if an average is available (at least one point has depth); false otherwise.

def find_depth_from(frame, depth_scale, face, markup_from, markup_to, p_average_depth):
    average_depth = 0
    n_points = 0
    for i in range(markup_from, markup_to+1):
        pt = face.part( i )
        if( pt.x <= 0 or pt.x >= frame.get_width() or pt.y <= 0 or pt.y >= frame.get_height() ):
             continue
        depth_in_pixels = frame.get_distance(pt.x, pt.y)
        average_depth += depth_in_pixels
        n_points += 1
    if( n_points == 0 ):
        return False, p_average_depth
    p_average_depth = average_depth / n_points
    return True, p_average_depth


# Returns whether the given 68-point facial landmarks denote the face of a real
# person (and not a picture of one), using the depth data in depth_frame.
# See markup_68 for an explanation of the point topology.
# NOTE: requires the coordinates in face align with those of the depth frame.

def validate_face(frame, depth_scale, face):
    # Collect all the depth information for the different facial parts

    # For the ears, only one may be visible -- we take the closer one!
    left_ear_depth = 100
    right_ear_depth = 100
    
    t1, right_ear_depth = find_depth_from( frame, depth_scale, face, markup_68.RIGHT_EAR, markup_68.RIGHT_1, right_ear_depth )
    t2, left_ear_depth = find_depth_from( frame, depth_scale, face, markup_68.LEFT_1, markup_68.LEFT_EAR, left_ear_depth )
    if( (not t1) and (not t2) ):
        return False
    ear_depth = min( right_ear_depth, left_ear_depth )

    t1, chin_depth = find_depth_from( frame, depth_scale, face, markup_68.CHIN_FROM, markup_68.CHIN_TO, 0 )
    if( (not t1) ):
        return False

    t1, nose_depth = find_depth_from( frame, depth_scale, face, markup_68.NOSE_TIP, markup_68.NOSE_TIP, 0 )
    if( (not t1) ):
        return False

    t1, right_eye_depth = find_depth_from( frame, depth_scale, face, markup_68.RIGHT_EYE_FROM, markup_68.RIGHT_EYE_TO, 0)
    if( (not t1) ):
        return False
    
    t1, left_eye_depth = find_depth_from( frame, depth_scale, face, markup_68.LEFT_EYE_FROM, markup_68.LEFT_EYE_TO, 0 ) 
    if( (not t1) ):
        return False

    eye_depth = min( left_eye_depth, right_eye_depth )

    t1, mouth_depth = find_depth_from( frame, depth_scale, face, markup_68.MOUTH_OUTER_FROM, markup_68.MOUTH_INNER_TO, 0 )
    if( (not t1) ):
        return False

    # // We just use simple heuristics to determine whether the depth information agrees with
    # // what's expected: that the nose tip, for example, should be closer to the camera than
    # // the eyes.

    # // These heuristics are fairly basic but nonetheless serve to illustrate the point that
    # // depth data can effectively be used to distinguish between a person and a picture of a
    # // person...

    # print("nose", nose_depth)
    # print("eye", eye_depth)
    # print("ear", ear_depth)
    # print("mouth", mouth_depth)
    # print("chin", chin_depth)

    if( nose_depth >= eye_depth ):
        return False
    if( eye_depth - nose_depth > 0.1 ):
        return False
    # if( ear_depth <= eye_depth ):
    #     return False
    if( mouth_depth <= nose_depth ):
        return False
    if( mouth_depth > chin_depth ):
        return False

    # // All the distances, collectively, should not span a range that makes no sense. I.e.,
    # // if the face accounts for more than 20cm of depth, or less than 2cm, then something's
    # // not kosher!

    x = max( { nose_depth, eye_depth, ear_depth, mouth_depth, chin_depth } )
    n = min( { nose_depth, eye_depth, ear_depth, mouth_depth, chin_depth } )


    if( x - n > 0.20 ):
        return False
    if( x - n < 0.01 ):
        return False

    return True

def main():
    print(dlib.DLIB_USE_CUDA)
    # Create a context object. This object owns the handles to all connected realsense devices
    pipe = rs.pipeline()

    # Configure streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    profile = pipe.start(config)

    # Each depth camera might have different units for depth pixels, so we get it here
    # Using the pipeline's profile, we can retrieve the device that the pipeline uses
    DEPTH_SENSOR = profile.get_device().first_depth_sensor()
    DEVICE_DEPTH_SCALE = DEPTH_SENSOR.get_depth_scale()
    print(DEVICE_DEPTH_SCALE)


    # The face detector we use is made using the classic Histogram of Oriented
    # Gradients (HOG) feature combined with a linear classifier, an image pyramid,
    # and sliding window detection scheme, using dlib's implementation of:
    #     One Millisecond Face Alignment with an Ensemble of Regression Trees by
    #     Vahid Kazemi and Josephine Sullivan, CVPR 2014
    # and was trained on the iBUG 300-W face landmark dataset (see
    # https://ibug.doc.ic.ac.uk/resources/facial-point-annotations/):
    #     C. Sagonas, E. Antonakos, G, Tzimiropoulos, S. Zafeiriou, M. Pantic.
    #     300 faces In-the-wild challenge: Database and results.
    #     Image and Vision Computing (IMAVIS), Special Issue on Facial Landmark Localisation "In-The-Wild". 2016.

    # You can get the trained model file from:
    # http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

    # Note that the license for the iBUG 300-W dataset excludes commercial use.
    # So you should contact Imperial College London to find out if it's OK for
    # you to use this model file in a commercial product.

    face_bbox_detector = dlib.get_frontal_face_detector()
    #face_bbox_detector = dlib.cnn_face_detection_model_v1("mmod_human_face_detector.dat")
    face_landmark_annotator = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # The 5-point landmarks model file can be used, instead. It's 10 times smaller and runs
    # faster, from:
    # http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2
    # But the validate_face() and render_face() functions will then need to be changed
    # to handle 5 points.

    # We need to map pixels on the color frame to a depth frame, so we can
    # determine their depth. The problem is that the frames may (and probably
    # will!) be of different resolutions, and so alignment is necessary.
    # See the rs-align example for a better understanding.
    # We align the depth frame so it fits in resolution with the color frame
    # since we go from color to depth.

    align_to_color = rs.align( rs.stream.color )

    # Display annotations in one of two colors: if the face is determined to be that of a real
    # person, it is "good". Otherwise, "bad".
    bad_color = dlib.rgb_pixel( 255, 0, 0 )
    good_color = dlib.rgb_pixel( 0, 255, 0 )

    win = dlib.image_window()
    

    while(not(win.is_closed())):
        data = pipe.wait_for_frames(); # Wait for next set of frames from the camera
        data = align_to_color.process( data )       # Replace with aligned frames
        depth_frame = data.get_depth_frame()
        color_frame = data.get_color_frame()
        
        #print(depth_frame.get_distance(320, 240))

        # Create a dlib image for face detection
        image = np.asanyarray(color_frame.get_data())

        # Detect faces: find bounding boxes around all faces, then annotate each to find its landmarks
        face_bboxes = face_bbox_detector( image )
        faces = []

        for bbox in face_bboxes:
            faces.append( face_landmark_annotator( image, bbox ))

        # Display it all on the screen
        win.clear_overlay()
        win.set_image( image )
        for face in faces:
            if validate_face(depth_frame, DEVICE_DEPTH_SCALE, face):
                win.add_overlay(face, good_color)
            else:
                win.add_overlay(face, bad_color)

    return 0

main()