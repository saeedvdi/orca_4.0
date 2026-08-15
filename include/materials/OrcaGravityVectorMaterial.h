#pragma once

#include "ADMaterial.h"
#include "MooseTypes.h"

class OrcaGravityVectorMaterial : public ADMaterial
{
    public:
    static InputParameters validParams();
    OrcaGravityVectorMaterial(const InputParameters & parameters);

    protected:
    void initQpStatefulProperties() override;
    void computeQpProperties() override;

    private:
    const RealVectorValue _gravity_input;
    ADMaterialProperty<RealVectorValue> & _gravity;
};
