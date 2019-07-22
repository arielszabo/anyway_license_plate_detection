import os
import pydarknet
from . import blurring_utils

if __name__ == "__main__":
    # todo: download config an weights ...

    coco_net = pydarknet.Detector(config=bytes("cfg/yolov3.cfg", encoding="utf-8"),
                                  weights=bytes("weights/yolov3.weights", encoding="utf-8"),
                                  p=0,
                                  meta=bytes("cfg/coco.data", encoding="utf-8"))

    # todo: load the video
    base_path = r'/content/drive/My Drive/Colab Notebooks/AnyWay_detection/'
    for file in os.listdir('{}/input_testing_files/'.format(base_path)):
        if 'Gtd8Rkd9JIc' in file:
            file_path = '{}/input_testing_files/{}'.format(base_path, file)
            file_output_path = '{}/output_testing_files/car_pilot_extended_frames_blur_only_coco_{}'.format(base_path,
                                                                                                            file)
            print(file)
            s_frame = 420
            e_frame = 2370
            all_frames_bounds = blurring_utils.find_all(video_path=file_path,
                                         darknet_model=coco_net,
                                         thresh=0.1,
                                         class_label=['car', 'person', 'motorbike',
                                                      'truck', 'bus'],
                                         start_frame=s_frame,
                                         end_frame=e_frame)

            blurring_utils.blur_the_video(video_path=file_path,
                                          output_path=file_output_path,
                                          frames_bounds=all_frames_bounds,
                                          start_frame=s_frame,
                                          end_frame=e_frame)




