
MAP Client Release Scripts
==========================

Scripts to make a release of MAP Client.
Each branch contains the definitions of the packages, plugins, and workflows required for that particular variant.
The *main* branch contains the scripts for the release process and each branch should update its own scripts from the main branch.
A variant branch should not edit the python scripts, each variant branch should only edit the following files:

* package_listing.txt
* plugin_listing.txt
* workflow_listing.txt

To make a request for new variant of release use this issue template:

https://github.com/hsorby/mapclientreleasescripts/issues/new?assignees=&labels=&projects=&template=new-variant-request.md&title=%5BNew+variant%5D+
