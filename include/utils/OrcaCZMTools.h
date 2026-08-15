#pragma once

#include "RankFourTensor.h"
#include "RankTwoTensor.h"
#include "libmesh/vector_value.h"
#include "MooseTypes.h"
#include "RotationMatrix.h"

namespace OrcaCZMTools
{
inline ADRealVectorValue
computedVnormdV(const ADRealVectorValue & V)
{
  return V / V.norm();
}

/// compute the derivative of the rotation matrix, R=FU^-1, using Chen and Wheeler 1993
inline ADRankFourTensor
computedRdF(const ADRankTwoTensor & R, const ADRankTwoTensor & U)
{
  const auto Uhat = U.trace() * RankTwoTensor::Identity() - U;
  unsigned int k, l, m, n, p, q;
  const auto Uhat_det = Uhat.det();

  ADRankFourTensor dR_dF;
  for (k = 0; k < 3; k++)
    for (l = 0; l < 3; l++)
      for (m = 0; m < 3; m++)
        for (n = 0; n < 3; n++)
        {
          dR_dF(k, l, m, n) = 0.;
          for (p = 0; p < 3; p++)
            for (q = 0; q < 3; q++)
              dR_dF(k, l, m, n) +=
                  R(k, p) * (Uhat(p, q) * R(m, q) * Uhat(n, l) - Uhat(p, n) * R(m, q) * Uhat(q, l));

          dR_dF(k, l, m, n) /= Uhat_det;
        }

  return dR_dF;
}

/// compute the derivative of F^-1 w.r.t. to F
ADRankFourTensor computedFinversedF(const ADRankTwoTensor & F_inv);

/// compute the area ratio betweeen the deformed and undeformed configuration, and its derivatives w.r.t. the deformation gradient, F
///@{
inline ADReal
computeAreaRatio(const ADRankTwoTensor & FinvT, const ADReal & J, const ADRealVectorValue & N)
{
  return J * (FinvT * N).norm();
}

inline ADRankTwoTensor
computeDAreaRatioDF(const ADRankTwoTensor & FinvT,
                    const ADRealVectorValue & N,
                    const ADReal & J,
                    const ADRankFourTensor & DFinv_DF)
{
  const auto Fitr_N = FinvT * N;
  const auto Fitr_N_norm = Fitr_N.norm();
  ADRankTwoTensor R2temp;
  for (unsigned int l = 0; l < 3; l++)
    for (unsigned int m = 0; m < 3; m++)
    {
      R2temp(l, m) = 0;
      for (unsigned int i = 0; i < 3; i++)
        for (unsigned int j = 0; j < 3; j++)
          R2temp(l, m) += Fitr_N(i) * DFinv_DF(j, i, l, m) * N(j);

      R2temp(l, m) *= J / Fitr_N_norm;
    }

  return J * FinvT * Fitr_N_norm + R2temp;
}
///@}

/// compute the normal componets of a vector
inline ADRealVectorValue
computeNormalComponents(const ADRealVectorValue & normal, const ADRealVectorValue & vector)
{
  return (normal * vector) * normal;
}

/// compute the tangent componets of a vector
inline ADRealVectorValue
computeTangentComponents(const ADRealVectorValue & normal, const ADRealVectorValue & vector)
{
  return vector - computeNormalComponents(normal, vector);
}

/// compute the czm reference rotation based on the normal in the undeformed configuration and the mesh dimension
inline ADRankTwoTensor
computeReferenceRotation(const ADRealVectorValue & normal, const unsigned int mesh_dimension)
{
  ADRankTwoTensor rot;
  switch (mesh_dimension)
  {
    case 3:
      rot = RotationMatrix::rotVec1ToVec2<true>(RealVectorValue(1, 0, 0), normal);
      break;
    case 2:
      rot = RotationMatrix::rotVec2DToX<true>(normal).transpose();
      break;
    case 1:
      rot = RankTwoTensor::Identity();
      break;
    default:
      mooseError("computeReferenceRotation: mesh_dimension value should be 1, 2 or, 3. You "
                 "provided " +
                 std::to_string(mesh_dimension));
  }
  return rot;
}
} // namespace OrcaCZMTools