![Figure](figures/page_7_figure_000.png)

Figure 2. Example results on ImageNet validation images. For each triplet, we show the masked image (left), our MAE reconstruction $^\dagger$ (middle), and the ground-truth (right). The masking ratio is 80 % , leaving only 39 out of 196 patches. More examples are in the appendix. $^\dagger$ As no loss is computed on visible patches, the model output on visible patches is qualitatively worse. One can simply overlay the output with the visible patches to improve visual quality. We intentionally opt not to do this, so we can more comprehensively demonstrate the method's behavior.

![Figure](figures/page_7_figure_002.png)

Figure 3. Example results on COCO validation images, using an MAE trained on ImageNet (the same model weights as in Figure 2 ). Observe the reconstructions on the two right-most examples, which, although different from the ground truth, are semantically plausible.

derstanding of parts, objects, and scenes. To overcome this difference and encourage learning useful features, we show that a simple strategy works well in computer vision: masking a very high portion of random patches. This strategy largely reduces redundancy and creates a challenging selfsupervisory task that requires holistic understanding beyond low-level image statistics. To get a qualitative sense of our reconstruction task, see Figures 2 – 4 .

( iii ) The autoencoder's decoder , which maps the latent representation back to the input, plays a different role between reconstructing text and images. In vision, the decoder reconstructs pixels , hence its output is of a lower semantic level than common recognition tasks. This is in contrast to language, where the decoder predicts missing words that contain rich semantic information. While in BERT the decoder can be trivial (an MLP) [ 14 ] , we found that for images, the decoder design plays a key role in determining the semantic level of the learned latent representations.

Driven by this analysis, we present a simple, effective, and scalable form of a masked autoencoder (MAE) for visual representation learning. Our MAE masks random patches from the input image and reconstructs the missing patches in the pixel space. It has an asymmetric encoderdecoder design. Our encoder operates only on the visible subset of patches (without mask tokens), and our decoder is

lightweight and reconstructs the input from the latent representation along with mask tokens (Figure 1 ). Shifting the mask tokens to the small decoder in our asymmetric encoder-decoder results in a large reduction in computation. Under this design, a very high masking ratio ( e.g. , 75 % ) can achieve a win-win scenario: it optimizes accuracy while allowing the encoder to process only a small portion ( e.g. , 25 % ) of patches. This can reduce overall pre-training time by $3\times$ or more and likewise reduce memory consumption, enabling us to easily scale our MAE to large models.

Our MAE learns very high-capacity models that generalize well. With MAE pre-training, we can train datahungry models like ViT-Large/-Huge [ 16 ] on ImageNet-1K with improved generalization performance. With a vanilla ViT-Huge model, we achieve 87.8 % accuracy when finetuned on ImageNet-1K. This outperforms all previous results that use only ImageNet-1K data. We also evaluate transfer learning on object detection, instance segmentation, and semantic segmentation. In these tasks, our pre-training achieves better results than its supervised pre-training counterparts, and more importantly, we observe significant gains by scaling up models. These observations are aligned with those witnessed in self-supervised pre-training in NLP [ 14 , 47 , 48 , 4 ] and we hope that they will enable our field to explore a similar trajectory.

2

