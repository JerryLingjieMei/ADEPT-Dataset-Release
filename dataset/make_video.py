import os


def make_mp4(config):
    video = config.video
    for i, exp in enumerate(sorted(os.listdir(video.frame_dir))):
        if i >= video.n_videos:
            break
        if exp == "masks" or exp.endswith(".yaml"):
            continue
        command = '/data/vision/billf/object-properties/local/bin/ffmpeg -r %d -pattern_type glob -i ' \
                  '\'%s/%s/*.png\' -pix_fmt yuv420p -vcodec libx264 -crf 0 %s.mp4 -y' \
                  % (video.fps, video.frame_dir, exp, video.output_dir)
        os.system(command)
        if video.save_gif:
            command = '/data/vision/billf/object-properties/local/bin/ffmpeg -r %d -pattern_type glob -i ' \
                      '\'%s/%s/*.png\'  %s.gif -y' \
                      % (video.fps, video.frame_dir, exp, video.output_dir)
            os.system(command)
        if video.save_ogv:
            command = '/data/vision/billf/object-properties/local/bin/ffmpeg -r %d -pattern_type glob -i ' \
                      '\'%s/%s/*.png\'  %s.ogv -y' \
                      % (video.fps, video.frame_dir, exp, video.output_dir)
            os.system(command)
