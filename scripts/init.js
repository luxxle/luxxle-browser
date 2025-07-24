// Copyright (c) 2019 The Brave Authors. All rights reserved.
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this file,
// you can obtain one at http://mozilla.org/MPL/2.0/.

const fs = require('fs')
const Log = require('../lib/logging')
const path = require('path')
const { spawnSync } = require('child_process')
const util = require('../lib/util')

Log.progress('Performing initial checkout of brave-core')

const luxxleCoreDir = path.resolve(__dirname, '..', 'src', 'luxxle')
const luxxleCoreRef = util.getProjectVersion('luxxle-core')

if (!fs.existsSync(path.join(luxxleCoreDir, '.git'))) {
  Log.status(`Cloning luxxle-core [${luxxleCoreRef}] into ${luxxleCoreDir}...`)
  fs.mkdirSync(luxxleCoreDir)
  util.runGit(luxxleCoreDir, ['clone', util.getNPMConfig(['projects', 'luxxle-core', 'repository', 'url']), '.'])
  util.runGit(luxxleCoreDir, ['checkout', luxxleCoreRef])
}
const luxxleCoreSha = util.runGit(luxxleCoreDir, ['rev-parse', 'HEAD'])
Log.progress(`luxxle-core repo at ${luxxleCoreDir} is at commit ID ${luxxleCoreSha}`)

let npmCommand = 'npm'
if (process.platform === 'win32') {
  npmCommand += '.cmd'
}

util.run(npmCommand, ['install'], { cwd: luxxleCoreDir })

util.run(npmCommand, ['run', 'sync' ,'--', '--init'].concat(process.argv.slice(2)), {
  cwd: luxxleCoreDir,
  env: process.env,
  stdio: 'inherit',
  shell: true,
  git_cwd: '.', })
