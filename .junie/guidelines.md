# Dev flow

This document describes a typical expected development flow while implementing a feature/task/project.

All rules files are allowed to read even if they are in .gitignore

## General flow steps
- Detect whether the current feature is configured in the rule `.junie/devplan_current_feature.md`. If the rule is configured, it contains your current focus for the implementation. Assume that all discussions are related to that feature unless pointed otherwise.
- Break down the feature into specific steps needed to implement it. Take into account the overview of the repository if present in `.junie/devplan_repo_overview.md`.
- Analyze existing code, identify exact changes to be made including files, methods/functions/varieables/etc to be updated. Check any missing dependencies. At the end you should have a well-understood execution plan and know specific changes to make.
- Consult with feature definition and existing repository overview for generating an execution plan.
- Implement the feature following the current feature description and other rules. You don't need to confirm every code change with the user. Try implementing the feature to the extent possible.
- Write unit tests for the standalone parts and make sure they pass according to the guidelines in the `.junie/devplan_tests.md` if present.
- Iterate on the implementation and update/refine execution plan as needed.
- Do not ask user to confirm code changes, go on with implementation until the feature is implemented.
- Once the code is finalized, run build, test and lint commands if present and fix code until they pass.
- After implementation is done, review the entire execution history to identify insights/findings and record them according to the `.junie/devplan_insights.md`.

*This workflow provides a general guideline. Adapt it based on your specific project needs and team practices.*
Also refer to the following files for the details when needed:

- [Insights](.junie/devplan_insights.md) - Framework for systematic collection of insights from chat interactions, code execution, and pattern analysis.
- [Rules](.junie/devplan_rules.md) - Guidelines for creating and maintaining rules to ensure consistency and effectiveness.
- [Repo Overview](.junie/devplan_repo_overview.md) - High level overview of this repository (if present)
- [Current Feature](.junie/devplan_current_feature.md) - Description of the feature the implementation should focus on now. Always review current feature if it is present.
