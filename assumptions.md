# Model assumptions

The model assumes that the eye is 
1. a sphere, radius 12mm;
2. optically a pinhole camera, with the focus at the pupil and a focal length of 24mm; this is the model assumption for the fundus images which are used as inputs.

This is clearly a crude approximation. We can calculate how a position in the eye maps to a position on the image plane under such a simple approximation. Considering a single plane for simplicity, where:
- B is a source point on the retina, with angle $\alpha$;
- E is a target point in the image, with distance ${Lp}$ to the centre of the image

Then:
- $\tan(\beta) = L_p/d = \text{BC}/\text{AC}$
- $\text{BC} = r\sin(\gamma)$
- $\text{AC} = r - r\cos(\gamma)$
- $\Rarrow \tan(\beta) = \mathfrac{r\sin(\gamma)}{r(1-\cos(\gamma)}$
- $L_p = \mathfrac{d\sin(\gamma}{1-\cos(\gamma)} = \mathfrac{d\sin(\pi-\alpha)}{1-\cos(\pi-\alpha)} = \mathfrac{d\sin(\alpha)}{1+\cos(\alpha)}$.

This expression is used to remap the input image target pixels, back to an equirectangular projection of source retina angles. Given the resulting equirectangular representation of the retinal pixels, we can "gore" this map by breaking it up into segments of longitude, and projecting each segment about a central meridian.

