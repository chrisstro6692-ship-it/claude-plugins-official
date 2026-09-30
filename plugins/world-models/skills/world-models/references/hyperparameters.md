# World Models: architectures and hyperparameters

Numbers from Ha & Schmidhuber, *World Models* (2018), and its appendix. The
parameter counts below were re-derived from the stated architectures and match
the paper exactly, so they work as a check that a reimplementation is faithful.

## V: convolutional VAE

Input is a 64×64×3 frame scaled to [0, 1]. All convolutions use stride 2 and
no padding.

| Stage | Layer | Output |
|---|---|---|
| Encoder | conv 32, 4×4, ReLU | 31×31×32 |
| | conv 64, 4×4, ReLU | 14×14×64 |
| | conv 128, 4×4, ReLU | 6×6×128 |
| | conv 256, 4×4, ReLU | 2×2×256 → flatten 1024 |
| Latent | dense → μ (N_z), dense → log σ² (N_z) | N_z |
| Decoder | dense N_z → 1024, reshape 1×1×1024 | 1×1×1024 |
| | deconv 128, 5×5, ReLU | 5×5×128 |
| | deconv 64, 5×5, ReLU | 13×13×64 |
| | deconv 32, 6×6, ReLU | 30×30×32 |
| | deconv 3, 6×6, sigmoid | 64×64×3 |

- Loss: summed squared-error reconstruction plus KL, with the KL clamped from
  below at `kl_tolerance × N_z` (kl_tolerance = 0.5), which works as free bits.
- N_z = 32 (CarRacing) gives **4,348,547** parameters. N_z = 64 (Doom) gives
  **4,446,915**.

## M: MDN-RNN

- An LSTM whose input is `[z_t, a_t]`. It has 256 hidden units for CarRacing
  and 512 for Doom.
- The MDN head is a dense layer from h to `3 × K × N_z` outputs, with K = 5
  mixtures. **Each latent dimension has its own 5-component mixture**, with its
  own mixture weights, means, and log-stds. It is a factorized mixture, not one
  joint mixture over the whole vector.
- Doom adds one output for the `done` logit (sigmoid, BCE loss).
- CarRacing: LSTM `4·256·(35+256+1)` = 299,008 plus head `257·480` = 123,360,
  for **422,368** in total.
- Doom: **1,678,785** in the paper. The scaffold's PyTorch model (65 inputs,
  512 hidden units, and a `3·5·64 + 1` = 961-output head) gives exactly that
  count.
- PyTorch's `nn.LSTM` keeps two bias vectors (`b_ih` and `b_hh`). For
  CarRacing, that makes the scaffold's count 423,392, which is `4 × 256` above
  the single-bias figure. That's expected.
- Temperature: logits / τ, σ × √τ.

## C: linear controller

- `a_t = tanh(W_c [z_t, h_t] + b_c)`, then mapped to the action space.
- CarRacing: 3 actions (steer ∈ [-1, 1], gas ∈ [0, 1], brake ∈ [0, 1]).
  3 × (32 + 256) + 3 = **867** parameters.
- Doom Take Cover: 1 output, thresholded to left / stay / right. The reported
  **1,088** equals the weight count when C also reads the LSTM cell state
  (64 + 512 + 512 inputs). The scaffold's `controller_inputs = "zhc"` has
  1,089 parameters because it adds a bias.

## CMA-ES

- Population 64. Fitness is the mean return over 16 rollouts per candidate.
- CarRacing trains in the real environment. Doom trains in the dream at
  τ = 1.15 and is evaluated in the real environment.
- The paper evaluates on 100 random rollouts and reports mean ± std.

## Data

- 10,000 random-policy rollouts for each environment.
- CarRacing: 1000 steps max. The bottom HUD rows are cropped before resizing to
  64×64.
- Doom Take Cover: 2100 steps max. It counts as solved when the average
  survival over 100 rollouts is above 750.

## Results to sanity-check against

| Setup | Score |
|---|---|
| CarRacing, C sees z only | 632 ± 251 |
| CarRacing, z only, one hidden layer in C | 788 ± 141 |
| CarRacing, z and h | **906 ± 21** (solved: > 900) |
| Doom, dream-trained at τ = 1.15, real env | **1092 ± 556** (solved: > 750) |
| Doom, random policy | 210 ± 108 |
