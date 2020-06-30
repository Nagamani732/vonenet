import torch
import torch.nn as nn
import os
import requests

from .vonenet import VOneNet


def get_model(model_arch=None, pretrained=True, **kwargs):
    """
    Returns a VOneNet model.
    Select pretrained=True for returning one of the 3 pretrained models.
    model_arch: string with identifier to choose the architecture of the back-end (resnet50, cornets, alexnet)
    """
    if pretrained:
        url = f'https://vonenet-models.s3.us-east-2.amazonaws.com/vone{model_arch.lower()}_e70.pth.tar'
        home_dir = os.environ['HOME']
        vonenet_dir = os.path.join(home_dir, '.vonenet')
        weightsdir_path = os.path.join(vonenet_dir, f'vone{model_arch.lower()}_e70.pth.tar')
        if not os.path.exists(vonenet_dir):
            os.makedirs(vonenet_dir)
        if not os.path.exists(weightsdir_path):
            print('Downloading model weights to ', weightsdir_path)
            r = requests.get(url, allow_redirects=True)
            open(weightsdir_path, 'wb').write(r.content)

        ckpt_data = torch.load(weightsdir_path)

        stride = ckpt_data['flags']['stride']
        simple_channels = ckpt_data['flags']['simple_channels']
        complex_channels = ckpt_data['flags']['complex_channels']
        k_exc = ckpt_data['flags']['k_exc']

        noise_mode = ckpt_data['flags']['noise_mode']
        noise_scale = ckpt_data['flags']['noise_scale']
        noise_level = ckpt_data['flags']['noise_level']

        model = globals()[f'VOneNet'](model_arch=model_arch, stride=stride, k_exc=k_exc,
                                      simple_channels=simple_channels, complex_channels=complex_channels,
                                      noise_mode=noise_mode, noise_scale=noise_scale, noise_level=noise_level)
        model = nn.DataParallel(model)
        model.load_state_dict(ckpt_data['state_dict'])
    else:
        model = globals()[f'VOneNet'](model_arch=model_arch, **kwargs)
        nn.DataParallel(model)
    return model



