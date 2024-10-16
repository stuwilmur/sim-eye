# Model assumptions

The model assumes that the eye is 
1. a sphere, radius 12mm;
2. optically a pinhole camera, with the focus at the pupil and a focal length of 24mm; this is the model assumption for the fundus images which are used as inputs.

This is clearly a crude approximation. We can calculate how a position in the eye maps to a position on the image plane under such a simple approximation. Consider a single plane for simplicity, where:
- B is a source point on the retina, with angle $\alpha$;
- E is a target point in the image, with distance ${Lp}$ to the centre of the image;
- r is the eye radius = 12:

![geometry wide](https://github.com/user-attachments/assets/c0a7106f-c815-4391-b991-8bdbacf68833)
![geometry close](https://github.com/user-attachments/assets/31c9644d-517b-45f3-8270-59ff9f3f5e69)

The task is then to calculate the image distance $L_p$, given a retinal angle $\alpha$:  
```math
\displaylines{\tan(\beta) = L_p/d = \text{BC}/\text{AC},\\
\text{BC} = r\sin(\gamma),\\
\text{AC} = r - r\cos(\gamma)\\
\Rightarrow \tan(\beta) = \frac{r\sin(\gamma)}{r(1-\cos(\gamma)}\\
\Rightarrow L_p = \frac{d\sin(\gamma)}{1-\cos(\gamma)} = \frac{d\sin(\pi-\alpha)}{1-\cos(\pi-\alpha)} = \frac{d\sin(\alpha)}{1+\cos(\alpha)}}.
```

This expression is used to remap the input image target pixels, back to an equirectangular projection of source retina angles. Given the resulting equirectangular representation of the retinal pixels, we can "gore" this map by breaking it up into segments of longitude, and projecting each segment about a central meridian.

