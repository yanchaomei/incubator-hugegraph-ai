#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# if we don't want to exit after '|', remove "-o pipefail"
set -exo pipefail

GROUP="hugegraph"
# current repository name
REPO="${GROUP}-ai"
# release version (input by committer)
RELEASE_VERSION=$1
USERNAME=$2
PASSWORD=$3
# git release branch (check it carefully)
GIT_BRANCH="release-${RELEASE_VERSION}"

RELEASE_VERSION=${RELEASE_VERSION:?"Please input the release version behind script"}

WORK_DIR=$(
  cd "$(dirname "$0")"
  pwd
)
cd "${WORK_DIR}"
echo "In the work dir: $(pwd)"

# clean old dir then build a new one
rm -rf dist && mkdir -p dist/apache-${REPO}

# step1: package the source code
cd ../
git archive --format=tar.gz \
  --output="scripts/dist/apache-${REPO}/apache-${REPO}-incubating-${RELEASE_VERSION}-src.tar.gz" \
  --prefix="apache-${REPO}-incubating-${RELEASE_VERSION}-src/" "${GIT_BRANCH}" || exit

cd -

# step2: copy the binary file (Optional)
# Note: it's optional for project to generate binary package (skip this step if not need)
#cp -v ../../target/apache-${REPO}-incubating-"${RELEASE_VERSION}".tar.gz \
#  dist/apache-${REPO}

# step3: sign + hash
##### 3.1 sign in source & binary package
gpg --version 1>/dev/null
cd ./dist/apache-${REPO}
for i in *.tar.gz; do
  echo "$i" && gpg --armor --output "$i".asc --detach-sig "$i"
done

##### 3.2 Generate SHA512 file
shasum --version 1>/dev/null
for i in *.tar.gz; do
  shasum -a 512 "$i" | tee "$i".sha512
done

#### 3.3 check signature & sha512
echo "#### start to check signature & hashcode ####"
for i in *.tar.gz; do
  echo "$i"
  gpg --verify "$i".asc "$i"
done

for i in *.tar.gz; do
  echo "$i"
  shasum -a 512 --check "$i".sha512
done

# step4: upload to Apache-SVN
SVN_DIR="${GROUP}-svn-dev"
cd ../
rm -rfv ${SVN_DIR}

##### 4.1 pull from remote & copy files
svn co "https://dist.apache.org/repos/dist/dev/incubator/${GROUP}" ${SVN_DIR}
mkdir -p ${SVN_DIR}/"${RELEASE_VERSION}"
cp -v apache-${REPO}/*tar.gz* "${SVN_DIR}/${RELEASE_VERSION}"
cd ${SVN_DIR}

##### 4.2 check status first
svn status
svn add --parents "${RELEASE_VERSION}"/apache-${REPO}-*
# check status again
svn status

##### 4.3 commit & push files
if [ "$USERNAME" = "" ]; then
  svn commit -m "submit files for ${REPO} ${RELEASE_VERSION}"
else
  svn commit -m "submit files for ${REPO} ${RELEASE_VERSION}" \
    --username "${USERNAME}" --password "${PASSWORD}"
fi

echo "Finished all, please check all steps in script manually again!"
