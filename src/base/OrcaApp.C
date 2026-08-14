#include "OrcaApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "ModulesApp.h"
#include "MooseSyntax.h"

InputParameters
OrcaApp::validParams()
{
  InputParameters params = MooseApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

OrcaApp::OrcaApp(const InputParameters & parameters) : MooseApp(parameters)
{
  OrcaApp::registerAll(_factory, _action_factory, _syntax);
}

OrcaApp::~OrcaApp() {}

void
OrcaApp::registerAll(Factory & f, ActionFactory & af, Syntax & syntax)
{
  ModulesApp::registerAllObjects<OrcaApp>(f, af, syntax);
  Registry::registerObjectsTo(f, {"OrcaApp"});
  Registry::registerActionsTo(af, {"OrcaApp"});

  /* register custom execute flags, action syntax, etc. here */
}

void
OrcaApp::registerApps()
{
  registerApp(OrcaApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
extern "C" void
OrcaApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  OrcaApp::registerAll(f, af, s);
}
extern "C" void
OrcaApp__registerApps()
{
  OrcaApp::registerApps();
}
