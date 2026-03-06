186    Chapter 7. THE ZETA FUNCTION AND PRIME NUMBER THEOREM

which holds for $0 \le x < 1$, we find that

$$\log \zeta ( s ) = \log \prod _ { p } \frac { 1 } { 1 - p ^ { - s } } = \sum _ { p } \log \left( \frac { 1 } { 1 - p ^ { - s } } \right) = \sum _ { p , m } \frac { p ^ { - m s } } { m } .$$

Since the double sum converges absolutely, we need not specify the order of summation. See the Note at the end of this chapter. The formula then holds for all $\text{Re}(s) > 1$ by analytic continuation. Note that, by Theorem 6.2 in Chapter 3, $\log \zeta(s)$ is well defined in the simply connected half-plane $\text{Re}(s) > 1$, since $\zeta$ has no zeros there. Finally, it is clear that we have

$$\sum _ { p , m } \frac { p ^ { - m s } } { m } = \sum _ { n = 1 } ^ { \infty } c _ { n } n ^ { - s } ,$$

where $c_n = 1/m$ if $n = p^m$ and $c_n = 0$ otherwise.

The proof of the theorem we shall give depends on a simple trick that is based on the following inequality.

Lemma 1.4 If $\theta \in \mathbb{R}$, then $3+4\cos\theta+\cos2\theta \geq 0$.

This follows at once from the simple observation

$$3 + 4 \cos \theta + \cos 2 \theta = 2 ( 1 + \cos \theta ) ^ { 2 } .$$

Corollary 1.5 If $\sigma>1$ and $t$ is real, then

$$\log \left| \zeta ^ { 3 } ( \sigma ) \zeta ^ { 4 } ( \sigma + i t ) \zeta ( \sigma + 2 i t ) \right| \geq 0 .$$

Proof. Let $s = \sigma + i t$ and note that

$$Re\left(n^{-s}\right)=Re\left(e^{-(\sigma+i t) \log n}\right)=e^{-\sigma \log n} \cos (t \log n)=n^{-\sigma} \cos (t \log n) .$$

Therefore,

$$\begin{aligned}
& \log \left|\zeta^{3}(\sigma) \zeta^{4}(\sigma+i t) \zeta(\sigma+2 i t)\right| \\
= & 3 \log |\zeta(\sigma)|+4 \log |\zeta(\sigma+i t)|+\log |\zeta(\sigma+2 i t)| \\
= & 3 Re[\log \zeta(\sigma)]+4 Re[\log \zeta(\sigma+i t)]+Re[\log \zeta(\sigma+2 i t)] \\
= & \sum c_{n} n^{-\sigma}\left(3+4 \cos \theta_{n}+\cos 2 \theta_{n}\right),
\end{aligned}$$

where $\theta_n = t \log n$. The positivity now follows from Lemma 1.4, and the fact that $c_n \geq 0$.

