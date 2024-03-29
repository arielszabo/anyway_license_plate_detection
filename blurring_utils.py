import cv2
import datetime
import pydarknet


def box_size(y1, y2, x1, x2, image_shape):
    """
    Calculate the bounding box's size ration from the entire photo
    """
    return (abs(y2 - y1) * abs(x2 - x1)) / (image_shape[0] * image_shape[1])


def find_in_img(image_frame, darknet_model, class_labels, thresh=0.5,
                bound_size_thresh=0.5):
    darknet_image_frame = pydarknet.Image(image_frame)

    results = darknet_model.detect(darknet_image_frame,
                                   thresh=thresh,  # 0.00051,
                                   hier_thresh=.5, nms=.45)  # todo: change this thresh-params thresh=0.01 #0.00051,
    results_bounds = []
    for category, score, bounds in results:
        category = str(category.decode("utf-8"))
        if category.lower() in [label.lower() for label in class_labels]:
            x, y, w, h = bounds
            y1, y2 = int(y - h / 2), int(y + h / 2)
            x1, x2 = int(x - w / 2), int(x + w / 2)

            if box_size(y1, y2, x1, x2, image_shape=image_frame.shape) < bound_size_thresh:
                results_bounds.append((y1, y2, x1, x2))
    return results_bounds


def add_mask(image_frame, results_bounds):
    """
    Add a mask around the bounding box

    :param image_frame: [img] a single frame
    :param results_bounds:
    :return:
    """
    for (y1, y2, x1, x2) in results_bounds:
        cv2.rectangle(image_frame, (x1, y1), (x2, y2), (255, 0, 0), thickness=2)
    # cv2.putText(image_frame, category, (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))

    return image_frame


def add_blur(image_frame, results_bounds, expand=False):
    for (y1, y2, x1, x2) in results_bounds:
        if expand: # todo: put here the father function
            x1, x2, y1, y2 = expand_mask(image_shape=image_frame.shape,
                                         x_left=x1,
                                         x_right=x2,
                                         y_buttom=y1,
                                         y_top=y2,
                                         expand_amount=20)

        image_frame[y1:y2, x1:x2] = cv2.GaussianBlur(image_frame[y1:y2, x1:x2], (11, 11), cv2.BORDER_DEFAULT)

    return image_frame


def expand_mask(image_shape, x_left, x_right, y_buttom, y_top, expand_amount=5):
    max_x = image_shape[0]
    max_y = image_shape[1]

    expanded_x_right = x_right + expand_amount
    expanded_y_top = y_top + expand_amount
    expanded_x_left = x_left - expand_amount
    expanded_y_buttom = y_buttom - expand_amount

    if expanded_x_left < 0:  # min_x
        expanded_x_left = 0

    if expanded_y_buttom < 0:  # min_y
        expanded_y_buttom = 0

    if expanded_x_right > max_x:
        expanded_x_right = max_x

    if expanded_y_top > max_y:
        expanded_y_top = max_y

    return expanded_x_left, expanded_x_right, expanded_y_buttom, expanded_y_top


def get_video_params(capture_vid):
    """
    Extract the video size, fps and codec
    :param capture_vid: [open-cv's VideoCapture object]
    :return: width [int], height [int], fps [float], fourcc [int
    """
    width = int(capture_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture_vid.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # int(cap.get(cv2.CAP_PROP_FOURCC))

    return width, height, fps, fourcc


def find_all(video_path, darknet_model, thresh, class_labels=("vehicle registration plate", "Person"), start_frame=0,
             end_frame=None):
    s = datetime.datetime.now()
    video_capture = cv2.VideoCapture(video_path)

    if not end_frame:  # if it's None
        end_frame = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

    counter = 0
    frames_bounds = []
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if ret:
            if start_frame < counter < end_frame:

                if counter % 100 == 0:
                    print('{} frames processed after {}'.format(counter,
                                                                datetime.datetime.now() - s))

                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_results_bounds = find_in_img(image_frame=frame, darknet_model=darknet_model,
                                                   class_labels=class_labels, thresh=thresh)
                frames_bounds.append(frame_results_bounds)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            counter += 1
        else:
            break

    # Release everything if job is finished
    video_capture.release()
    cv2.destroyAllWindows()
    print('all frames took {}'.format(datetime.datetime.now() - s))
    return frames_bounds


def blur_the_video(video_path, output_path, frames_bounds, start_frame=0,
                   end_frame=None):
    s = datetime.datetime.now()
    cap = cv2.VideoCapture(video_path)

    if cap.isOpened():
        width, height, fps, fourcc = get_video_params(capture_vid=cap)
        print(width, height, fps, fourcc)

        if not end_frame:  # if it's None
            end_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        output = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        counter = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if start_frame < counter < end_frame:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # todo: add this a param and put the bounds from the loop
                    for i in range(-1, 2):
                        real_index = counter - start_frame
                        if 0 <= real_index + i < len(frames_bounds):
                            bounds = frames_bounds[real_index + i]

                            frame = add_blur(frame,
                                             bounds,
                                             expand=False)
                            #                             frame = add_mask(frame, bounds)

                    new_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    output.write(new_frame)

                    if counter % int(fps) == 0:
                        print('{} seconds processed after {}'.format(
                            counter / int(fps), datetime.datetime.now() - s))

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                counter += 1

            else:
                break
    # Release everything if job is finished
        output.release()
        print('{} frames took {}'.format(counter, datetime.datetime.now() - s))
    cap.release()
    cv2.destroyAllWindows()
