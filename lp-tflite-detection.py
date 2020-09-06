import os
import sys
import traceback
from os import listdir
from os.path import isfile, join
from os.path import splitext, basename

import cv2

from args import get_args
from src.label import Shape, writeShapes
from src.tflite_utils import load_model, detect_lp
from src.utils import im2single, get_model_memory_usage, get_logger


def adjust_pts(pts, lroi):
    return pts * lroi.wh().reshape((2, 1)) + lroi.tl().reshape((2, 1))


logger = get_logger(__name__)
args = get_args()

if __name__ == '__main__':
    args = get_args()
    if args.use_colab:
        from google.colab import drive

        drive.mount('/content/gdrive')
        OUTPUT_DIR = '/content/gdrive/My Drive/lpd/{}_{}_{}'.format(args.image_size, args.initial_sparsity,
                                                                    args.final_sparsity)
        if not os.path.isdir(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
        lp_model = '%s/%s_trained' % (OUTPUT_DIR, args.model)
        test_dir = '/content/gdrive/My Drive/lpd/test_images'
        output_dir = '{}/{}'.format(OUTPUT_DIR, 'results')
        if not os.path.isdir(output_dir): os.makedirs(output_dir)
try:
    lp_threshold = .5

    wpod_net_path = lp_model
    wpod_net = load_model(wpod_net_path)
    onlyfiles = ["{}/{}".format(test_dir, f) for f in listdir(test_dir) if isfile(join(test_dir, f))]
    print(onlyfiles)
    print('Searching for license plates using WPOD-NET')
    logger.info('Searching for license plates using WPOD-NET')

    for i, img_path in enumerate(onlyfiles):

        print('\t Processing %s' % img_path)
        logger.info('\t Processing %s' % img_path)

        bname = splitext(basename(img_path))[0]
        Ivehicle = cv2.imread(img_path)

        ratio = float(max(Ivehicle.shape[:2])) / min(Ivehicle.shape[:2])
        side = int(ratio * 288.)
        bound_dim = min(side + (side % (2 ** 4)), 608)
        print("\t\tBound dim: %d, ratio: %f" % (bound_dim, ratio))
        logger.info("\t\tBound dim: %d, ratio: %f" % (bound_dim, ratio))

        Llp, LlpImgs, _ = detect_lp(wpod_net, im2single(Ivehicle), bound_dim, 2 ** 4, (240, 80), lp_threshold)

        if len(LlpImgs):
            Ilp = LlpImgs[0]
            Ilp = cv2.cvtColor(Ilp, cv2.COLOR_BGR2GRAY)
            Ilp = cv2.cvtColor(Ilp, cv2.COLOR_GRAY2BGR)

            s = Shape(Llp[0].pts)

            cv2.imwrite('%s/%s_lp.png' % (output_dir, bname), Ilp * 255.)
            writeShapes('%s/%s_lp.txt' % (output_dir, bname), [s])
    model_size_gb = get_model_memory_usage(args.batch_size, wpod_net)
    print("Model size in gb is : {}".format(model_size_gb))
    logger.info("Model size in gb is : {}".format(model_size_gb))
    print("Model size in mb is : {}".format(model_size_gb / 1024))
    logger.info("Model size in mb is : {}".format(model_size_gb / 1024))
    print("Model size in mb is : {}".format(model_size_gb / (1024 * 1024)))
    logger.info("Model size in mb is : {}".format(model_size_gb / (1024 * 1024)))
    print("Mean inference time (in seconds) : {}".format(mean(inference_times)))
    logger.info("Mean inference time (in seconds) : {}".format(mean(inference_times)))
except:
    traceback.print_exc()
    sys.exit(1)

sys.exit(0)