import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

def exaggerate_face(image):
    """
    Exaggerates key facial features (eyes, forehead, chin) using MediaPipe landmarks.
    Args:
        image (numpy.ndarray): BGR image from OpenCV.
    Returns:
        numpy.ndarray: Modified image with exaggerated facial features.
    """
    try:
        h, w = image.shape[:2]
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            face_mesh.close()
            return image

        landmarks = results.multi_face_landmarks[0].landmark

        def to_pixel(p):
            return np.array([int(p.x * w), int(p.y * h)])

        left_eye = [to_pixel(landmarks[i]) for i in [33, 133, 160, 159, 158, 144, 153, 154, 155]]
        right_eye = [to_pixel(landmarks[i]) for i in [362, 263, 387, 386, 385, 373, 380, 374, 381]]
        forehead = [to_pixel(landmarks[i]) for i in [10, 338, 297, 332]]
        chin = [to_pixel(landmarks[i]) for i in [152, 176, 148]]

        exaggerated = image.copy()

        def scale_region(region_points, scale_factor):
            center = np.mean(region_points, axis=0).astype(int)
            scaled_points = []
            for pt in region_points:
                offset = pt - center
                scaled = center + offset * scale_factor
                scaled_points.append(scaled.astype(np.int32))
            return np.array(scaled_points, np.int32)

        def warp_region(src_pts, dst_pts):
            hull_src = cv2.convexHull(np.array(src_pts))
            hull_dst = cv2.convexHull(np.array(dst_pts))

            rect = cv2.boundingRect(hull_src)
            subdiv = cv2.Subdiv2D(rect)
            for pt in hull_src:
                subdiv.insert(tuple(pt[0]))

            triangles = subdiv.getTriangleList()
            triangles = np.array(triangles, dtype=np.int32)

            for t in triangles:
                src_tri = []
                dst_tri = []
                for i in range(0, 6, 2):
                    x, y = t[i], t[i + 1]
                    if rect[0] <= x < rect[0] + rect[2] and rect[1] <= y < rect[1] + rect[3]:
                        pt = np.array([x, y])
                        src_tri.append(pt)
                        idx = np.argmin([np.linalg.norm(pt - s) for s in src_pts])
                        dst_tri.append(dst_pts[idx])
                if len(src_tri) == 3 and len(dst_tri) == 3:
                    warp_triangle(image, exaggerated, np.array(src_tri), np.array(dst_tri))

        def warp_triangle(img1, img2, t1, t2):
            r1 = cv2.boundingRect(t1)
            r2 = cv2.boundingRect(t2)

            t1_rect = []
            t2_rect = []
            for i in range(3):
                t1_rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
                t2_rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))

            mask = np.zeros((r2[3], r2[2], 3), dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.int32(t2_rect), (1.0, 1.0, 1.0), 16, 0)

            img1_rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
            size = (r2[2], r2[3])

            mat = cv2.getAffineTransform(np.float32(t1_rect), np.float32(t2_rect))
            warped = cv2.warpAffine(img1_rect, mat, size, None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * (1 - mask) + warped * mask

        # Apply exaggerated transformations
        left_eye_scaled = scale_region(left_eye, 1.4)
        right_eye_scaled = scale_region(right_eye, 1.4)
        forehead_scaled = scale_region(forehead, 1.2)
        chin_scaled = scale_region(chin, 0.8)

        warp_region(left_eye, left_eye_scaled)
        warp_region(right_eye, right_eye_scaled)
        warp_region(forehead, forehead_scaled)
        warp_region(chin, chin_scaled)

        face_mesh.close()
        return exaggerated

    except Exception as e:
        print(f"❌ Error exaggerating face: {e}")
        return image


