#include "OrcaCZMTools.h"

namespace OrcaCZMTools
{
ADRankFourTensor
computedFinversedF(const ADRankTwoTensor & F_inv)
{
  usingTensorIndices(i_, j_, k_, l_);
  return -F_inv.times<i_, k_, j_, l_>(F_inv.transpose());
}
} // namespace OrcaCZMTools