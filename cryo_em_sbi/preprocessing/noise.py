import numpy as np
import torch


def add_noise(img, preproc_params, radius_coef):

    def circular_mask(n_pixels, radius):

        grid = torch.linspace(-0.5 * (n_pixels - 1), 0.5 * (n_pixels - 1), n_pixels)
        r_2d = grid[None, :]**2 + grid[:, None]**2
        mask = r_2d < radius**2

        return mask
        
    mask = circular_mask(n_pixels=img.shape[0], radius=img.shape[0] * radius_coef)

    signal_std = img[mask].pow(2).mean().sqrt()
    noise_std = signal_std / np.sqrt(preproc_params["SNR"])

    img_noise = img + torch.distributions.normal.Normal(0, noise_std).sample(img.shape)

    return img_noise


def add_noise_to_dataset(dataset, preproc_params):

    images_with_noise = torch.empty_like(dataset, device=preproc_params["DEVICE"])
    n_pixels = int(np.sqrt(dataset.shape[1]))

    for i in range(dataset.shape[0]):

        tmp_image = add_noise(dataset[i].reshape(n_pixels, n_pixels), preproc_params)

        images_with_noise[i] = tmp_image.reshape(1, -1).to(preproc_params["DEVICE"])

    return images_with_noise
