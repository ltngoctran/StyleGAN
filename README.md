# StyleGAN

Project from MVA Course Deep Learning for Restoration and Synthesis Images

In this project, we do some experiments to explore the linearity and disentanglement of the latent spaces (in both $\mathcal{Z}$ and $\mathcal{W}$ space). We use pre-trained model and dataset FFHQ.

## 1. File.ipynb
```bash 
StyleGan2_Final.ipynb 
``` 
includes $\mathbf{z}$ and $\mathbf{w}$ interpolation. Moreover, we can change the number of layers and then see the affect of layers in the attribute of generated images.

```bash
InterfaceGAN.ipynb
```
InterfaceGAN is the second approach to study the disentanglement of the latent space. With this file, we can change both the direction of latent vectors $\mathbf{z}$ and $\mathbf{w}$ and see how images change.

## 2. Folders and other files

images: include the figures and results in report

papers: include file pdf of three main articles is used for this report.

mov.mp4: the video obtained when interpolating latent vectors.