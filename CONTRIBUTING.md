# Contributing

Use Python 3.11 or later. Work from a virtual environment if installing the
package; the test suite also runs directly from the checkout without installation.

Run `python3 -m unittest discover -s tests -v` before sending a pull request.
Use four-space indentation, descriptive snake_case names, and type annotations
for public functions. Keep physical geometry separate from presentation code.

For geometry changes, add tests that verify dimensions, connectivity, or fit
rather than only comparing serialized SVG text. Include a generated example and
describe any physical assembly checks. Do not claim printer validation based on
software tests alone.

Keep commits focused, with imperative subjects such as `Add page alignment marks`.
Pull requests should explain the user problem, the resulting behavior, and the
checks performed. Link a relevant issue when one exists.

Use synthetic designs and measurements in examples. Do not include credentials,
customer files, private records, or code you do not have permission to contribute.
Retain third-party attribution and license notices where applicable.
