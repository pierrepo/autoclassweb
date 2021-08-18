# How to release

## Setup

Install required packages:
```bash
$ conda env create -f environment.yml
```

Or if needed, update your conda environment:
```bash
$ conda env update -f environment.yml
```

For Zenodo integration, see [Making Your Code Citable](https://guides.github.com/activities/citable-code/).

## Lock dependencies (if needed)

```
$ conda env export -n autoclassweb --no-builds  | grep -v "^prefix:" > environment-lock.yml
$ git commit -a -m "Update conda dependencies"
```

## Update version number

We use `bump2version` to update and synchronize the version number across different files.

For patch update (x.y.z → x.y.**z+1**):
```
$ bump2version --verbose --config-file devtools/bumpversion.cfg patch
```

For minor update (x.y.z → x.**y+1**.0):
```
$ bump2version --verbose --config-file devtools/bumpversion.cfg minor
```

For major update (x.y.z → **x+1**.0.0):
```
$ bump2version --verbose --config-file devtools/bumpversion.cfg major
```

Remark:

1. For a dry run with `bump2version`, use option `-n`.
2. `bump2version` will fail if the git working directory is not clean, i.e. all changes are not commited.

Once version number is updated, push everything to GitHub:
```
$ git push origin
$ git push origin --tags
```


## Add new release on GitHub

On [GitHub release page](https://github.com/pierrepo/autoclassweb/releases) :

- Click the *Draft a new release* button.
- Select the latest version as *tag version*.
- Add release version as *Release title* (e.g.: v1.3.7).
- Copy and paste the content of the `CHANGELOG.md` in the *Describe this release* field.
- Hit the *Publish release* button :rocket:.


## Zenodo integration

After the creation of the new release in GitHub, check the archive has been creating on [Zenodo](https://doi.org/10.5281/zenodo.5215902).


## Publish docker image 

Docker images of AutoClassWeb are hosted in the [Biocontainers](https://biocontainers.pro/) docker repository:

<https://hub.docker.com/r/biocontainers/autoclassweb>

To push new images:

-  Clone <https://github.com/BioContainers/containers>
-  Add the Dockerfile for the new release in the `autoclassweb` subdirectory
-  Make a pull request for merging.

