import numpy as np
import torch


def gen_quat():
    """Generate a random quaternion.
    
    Returns:
        quat (np.ndarray): Random quaternion
    
    """
    count = 0
    while count < 1:
        quat = np.random.uniform(
            -1, 1, 4
        )  # note this is a half-open interval, so 1 is not included but -1 is
        norm = np.sqrt(np.sum(quat**2))

        if 0.2 <= norm <= 1.0:
            quat /= norm
            count += 1

    return quat


def gen_img(coord, image_params):
    """Generate an image from a set of coordinates.
    
    Args:
        coord (torch.Tensor): Coordinates of the atoms in the image
        image_params (dict): Dictionary containing the image parameters
            N_PIXELS (int): Number of pixels along one image size.
            PIXEL_SIZE (float): Pixel size in Angstrom
            SIGMA (float or list): Standard deviation of the Gaussian function used to model electron density.
            ELECWAVE (float): Electron wavelength in Angstrom
    
    Returns:
        image (torch.Tensor): Image generated from the coordinates
    """

    n_atoms = coord.shape[1]

    if isinstance(image_params["SIGMA"], float):
        atom_sigma = image_params["SIGMA"]

    elif isinstance(image_params["SIGMA"], list) and len(image_params["SIGMA"]) == 2:
        atom_sigma = np.random.uniform(
            low=image_params["SIGMA"][0], high=image_params["SIGMA"][1]
        )

    else:
        raise ValueError(
            "SIGMA should be a single value or a list of [min_sigma, max_sigma]"
        )

    norm = 1 / (2 * torch.pi * atom_sigma**2 * n_atoms)

    grid_min = -image_params["PIXEL_SIZE"] * (image_params["N_PIXELS"] - 1) * 0.5
    grid_max = (
        image_params["PIXEL_SIZE"] * (image_params["N_PIXELS"] - 1) * 0.5
        + image_params["PIXEL_SIZE"]
    )

    grid = torch.arange(grid_min, grid_max, image_params["PIXEL_SIZE"])

    gauss_x = torch.exp(-0.5 * (((grid[:, None] - coord[0, :]) / atom_sigma) ** 2))

    gauss_y = torch.exp(-0.5 * (((grid[:, None] - coord[1, :]) / atom_sigma) ** 2))

    image = torch.matmul(gauss_x, gauss_y.T) * norm

    return image
