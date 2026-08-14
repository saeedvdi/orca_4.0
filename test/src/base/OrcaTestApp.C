//* This file is part of the MOOSE framework
//* https://mooseframework.inl.gov
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#include "OrcaTestApp.h"
#include "OrcaApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "MooseSyntax.h"

InputParameters
OrcaTestApp::validParams()
{
  InputParameters params = OrcaApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

OrcaTestApp::OrcaTestApp(const InputParameters & parameters) : MooseApp(parameters)
{
  OrcaTestApp::registerAll(
      _factory, _action_factory, _syntax, getParam<bool>("allow_test_objects"));
}

OrcaTestApp::~OrcaTestApp() {}

void
OrcaTestApp::registerAll(Factory & f, ActionFactory & af, Syntax & s, bool use_test_objs)
{
  OrcaApp::registerAll(f, af, s);
  if (use_test_objs)
  {
    Registry::registerObjectsTo(f, {"OrcaTestApp"});
    Registry::registerActionsTo(af, {"OrcaTestApp"});
  }
}

void
OrcaTestApp::registerApps()
{
  registerApp(OrcaApp);
  registerApp(OrcaTestApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
// External entry point for dynamic application loading
extern "C" void
OrcaTestApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  OrcaTestApp::registerAll(f, af, s);
}
extern "C" void
OrcaTestApp__registerApps()
{
  OrcaTestApp::registerApps();
}
