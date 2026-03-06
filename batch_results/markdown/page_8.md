236

9 Calculus and Number Theory

Proof Firstly, from ( 9.14 ) we get

$$\begin{aligned}
\left|P_{n}-\sum_{k=1}^{n} \frac{\mu (k)}{k^{2}}\right| & =\left|\sum_{k=1}^{n} \mu (k)\left(\frac{1}{n^{2}}\left\lfloor\frac{n}{k}\right\rfloor^{2}-\frac{1}{k^{2}}\right)\right| \\
& \leq  \sum_{k=1}^{n}\left|\frac{1}{k^{2}}-\frac{1}{n^{2}}\left\lfloor\frac{n}{k}\right\rfloor^{2}\right| .
\end{aligned}\quad (9.15)$$

In order to estimate the last sum above, we claim that, given natural numbers $n$ and $k$ such that $1 \leq  k \leq  n$ , we have

$$\left| { \frac { 1 } { k ^ { 2 } } } - { \frac { 1 } { n ^ { 2 } } } \left[ { \frac { n } { k } } \right] ^ { 2 } \right| < { \frac { 2 } { n k } } - { \frac { 1 } { n ^ { 2 } } } .$$

Indeed,

$$\begin{array} { r l } { \frac { n } { k } - 1 < \left\lfloor \frac { n } { k } \right\rfloor } & { \leq  \frac { n } { k } \Rightarrow \frac { n ^ { 2 } } { k ^ { 2 } } - \frac { 2 n } { k } + 1 < \left\lfloor \frac { n } { k } \right\rfloor ^ { 2 } \leq  \frac { n ^ { 2 } } { k ^ { 2 } } } \\ & { \Rightarrow \frac { 1 } { k ^ { 2 } } - \frac { 2 } { k n } + \frac { 1 } { n ^ { 2 } } < \frac { 1 } { n ^ { 2 } } \left\lfloor \frac { n } { k } \right\rfloor ^ { 2 } \leq  \frac { 1 } { k ^ { 2 } } } \\ & { \Rightarrow 0 \leq  \frac { 1 } { k ^ { 2 } } - \frac { 1 } { n ^ { 2 } } \left\lfloor \frac { n } { k } \right\rfloor ^ { 2 } < \frac { 2 } { k n } - \frac { 1 } { n ^ { 2 } } , } \end{array}$$

as wished.

Back to (9.15), we obtain from the above estimates that

$$\left| P _ { n } - \sum _ { k = 1 } ^ { n } { \frac { \mu  ( k ) } { k ^ { 2 } } } \right| < \sum _ { k = 1 } ^ { n } \left( { \frac { 2 } { n k } } - { \frac { 1 } { n ^ { 2 } } } \right) = { \frac { 2 } { n } } \sum _ { k = 1 } ^ { n } { \frac { 1 } { k } } - { \frac { 1 } { n } } .$$

Now, from L'Hôpital's rule we get

$$\frac { 2 } { n } \sum _ { k = 1 } ^ { n } \frac { 1 } { k } < \frac { 2 } { n } \left( 1 + \int _ { 1 } ^ { n } \frac { 1 } { t } d t \right) = \frac { 2 } { n } ( \log n + 1 ) \to 0$$

as $n \to +\infty$. Hence,

$$\lim _ { n \to + \infty } \left( \frac { 2 } { n } \sum _ { k = 1 } ^ { n } \frac { 1 } { k } - \frac { 1 } { n } \right) = 0 ,$$

and our previous estimates assure that

