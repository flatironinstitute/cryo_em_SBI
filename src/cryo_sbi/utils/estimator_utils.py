import torch
import json
from cryo_sbi.inference.models import build_models


def sample_posterior(estimator, images, num_samples, batch_size=100, device="cpu"):
    """Samples from the posterior distribution

    Args:
        estimator (torch.nn.Module): The posterior to use for sampling.
        images (torch.Tensor): The images used to condition the posterio.
        num_samples (int): The number of samples to draw
        batch_size (int, optional): The batch size to use. Defaults to 100.
        device (str, optional): The device to use. Defaults to "cpu".

    Returns:
        torch.Tensor: The samples
    """

    theta_samples = []

    if images.shape[0] > batch_size and batch_size > 0:
        images = torch.split(images, split_size_or_sections=batch_size, dim=0)
    else:
        batch_size = images.shape[0]
        images = [images]

    with torch.no_grad():
        for image_batch in images:
            samples = estimator.sample(
                image_batch.to(device, non_blocking=True), shape=(num_samples,)
            ).cpu()
            theta_samples.append(samples.reshape(-1, image_batch.shape[0]))

    return torch.cat(theta_samples, dim=1)


def compute_latent_repr(estimator, images, batch_size=100, device="cpu"):
    """Computes the latent representation of images.

    Args:
        estimator (torch.nn.Module): Posterior model for which to compute the latent representation.
        images (torch.Tensor): The images to compute the latent representation for.
        batch_size (int, optional): The batch size to use. Defaults to 100.
        device (str, optional): The device to use. Defaults to "cpu".

    Returns:
        torch.Tensor: The latent representation of the images.
    """

    latent_space_samples = []

    if images.shape[0] > batch_size and batch_size > 0:
        images = torch.split(images, split_size_or_sections=batch_size, dim=0)
    else:
        batch_size = images.shape[0]
        images = [images]

    with torch.no_grad():
        for image_batch in images:
            samples = estimator.embedding(
                image_batch.to(device, non_blocking=True)
            ).cpu()
            latent_space_samples.append(samples.reshape(image_batch.shape[0], -1))

    return torch.cat(latent_space_samples, dim=0)


def load_estimator(config_file_path, estimator_path, device="cpu"):
    """Loads a trained estimator.

    Args:
        config_file_path (str): Path to the config file used to train the estimator.
        estimator_path (str): Path to the estimator.
        device (str, optional): The device to use. Defaults to "cpu".

    Returns:
        torch.nn.Module: The loaded estimator.
    """

    train_config = json.load(open(config_file_path))
    estimator = build_models.build_npe_flow_model(train_config)
    estimator.load_state_dict(
        torch.load(estimator_path, map_location=torch.device(device))
    )
    estimator.to(device)
    estimator.eval()

    return estimator
