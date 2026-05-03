# 个人项目 Git 规范指南

> 单人项目也要有 Git 纪律。清晰的提交历史就是你的开发日记——三个月后回溯 Bug、复盘设计思路，全靠它。

---

## 速查：你应该看哪部分？

| 你现在想做什么 | 直接跳到 |
|---|---|
| 刚开始用 Git，想建立规范 | [第一部分：日常习惯](#第一部分日常习惯) |
| 提交信息不知道怎么写 | [提交信息怎么写](#提交信息怎么写) |
| 分支什么时候该建、怎么命名 | [分支怎么用](#分支怎么用) |
| 提交历史很乱，想整理 | [保持历史整洁](#保持历史整洁) |
| 遇到问题了想救命 | [第三部分：踩坑自救](#第三部分踩坑自救) |
| 想让 Git 更顺手 | [第四部分：配置优化](#第四部分配置优化) |

---

## 第一部分：日常习惯

### 提交信息怎么写

**为什么重要？** 提交历史是你唯一的"时间机器"。三个月后你看到 `fix bug` 根本不知道改了什么，但看到 `fix: resolve null pointer when user not logged in` 就能立刻回忆起上下文。

**格式（单人项目简化版）：**

```
<类型>: <做了什么>
```

**类型一览：**

| 类型 | 什么时候用 | 示例 |
|---|---|---|
| `feat` | 加了新功能 | `feat: add user login page` |
| `fix` | 修了 Bug | `fix: resolve crash on empty input` |
| `refactor` | 改了代码结构，但功能不变 | `refactor: extract validation to utils` |
| `docs` | 改了文档 | `docs: update README with setup guide` |
| `style` | 调了格式，不影响功能 | `style: format code with prettier` |
| `perf` | 优化了性能 | `perf: lazy load image components` |
| `test` | 加了测试 | `test: add unit tests for auth module` |
| `chore` | 改了依赖、配置等杂项 | `chore: upgrade react to v19` |
| `init` | 项目初始化 | `init: scaffold project with vite` |
| `wip` | 进行中，还没完成 | `wip: add dashboard layout` |

**三条铁律：**

1. **说清楚做了什么**——`fix: resolve crash on empty input` ✅ vs `fix bug` ❌
2. **用祈使句、现在时**——`add feature` ✅ vs `added feature` ❌
3. **一行不超过 72 字符**——太长在终端里会换行，很难看

**复杂变更可以写多行：**

```
feat: add order export to CSV

- Implement CSV generation with proper escaping
- Add date range filter for export
- Support both simplified and traditional Chinese headers

This allows shop owners to export order data for
accounting purposes, which was the #1 requested feature.
```

**想自动强制规范？** 安装 commitlint + husky，每次 commit 自动检查格式：

```bash
npm install -D @commitlint/cli @commitlint/config-conventional husky
npx husky init
echo 'npx --no commitlint --edit "$1"' > .husky/commit-msg
```

---

### 提交粒度：一次提交该包含多少？

**原则：一个提交 = 一个逻辑变更。**

为什么？因为这样每个提交都能独立回退。如果你把 10 个不相关的改动塞进一个提交，想撤销其中一个时就很痛苦。

```
✅ 一次提交只做一件事：加登录功能、修一个 Bug、更新一段文档
❌ 一次提交包含：登录功能 + 修 Bug + 更新依赖 + 格式调整
```

**实际操作——按逻辑分批提交：**

```bash
# ❌ 偷懒做法：全选一次提交
git add .
git commit -m "update"

# ✅ 正确做法：按功能分批
git add src/auth/login.ts
git commit -m "feat: add login form validation"

git add src/auth/register.ts
git commit -m "feat: add registration form"

git add tests/auth.test.ts
git commit -m "test: add unit tests for auth module"
```

---

### 分支怎么用

**为什么需要分支？** 如果你在 main 上直接开发一个新功能，开发到一半发现方案不行想放弃，就得一个个回退提交。有了分支，放弃只需删掉分支，main 完全不受影响。

**单人项目的分支策略非常简单：**

```
main → 始终是"能跑的版本"，这就是你唯一的长期分支
```

**什么时候需要建分支？**

| 场景 | 建议 |
|---|---|
| 改个错别字、调个样式 | 直接在 main 上提交就行 |
| 尝试一个不确定的新方案 | 建分支，不行就删 |
| 需要开发几天的大功能 | 建分支，完成后合并 |
| 修一个复杂的 Bug | 建分支，避免和功能开发混在一起 |

**分支命名格式：`类型/简短描述`**

```
feature/add-dark-mode       → 新功能
experiment/try-redis-cache  → 实验性尝试
fix/login-timeout           → Bug 修复
chore/update-deps           → 杂务
```

**用完就删，保持干净：**

```bash
# 合并完成后删除分支
git branch -d feature/add-dark-mode

# 查看哪些分支已经合并了，可以安全删除
git branch --merged

# 一键清理（保留 main）
git branch --merged | grep -v '\*\|main' | xargs -n 1 git branch -d
```

---

### 保持历史整洁

**为什么重要？** 杂乱的提交历史（一堆 `fix typo`、`wip`、`update`）会让 `git log` 变得毫无参考价值。整洁的历史就像一本有目录的书，随时能翻到你想找的内容。

**方法一：提交前用交互式 rebase 整理**

开发过程中难免产生杂乱提交。合并分支前，用 `rebase -i` 把它们整理干净：

```bash
# 整理最近 3 个提交
git rebase -i HEAD~3
```

编辑器会列出这些提交，你可以对每个提交选择操作：

| 操作 | 效果 | 什么时候用 |
|---|---|---|
| `pick` | 保留这个提交 | 默认 |
| `squash` | 合并到上一个提交，保留两个的提交信息 | 把"修 typo"合并到"加功能"里 |
| `fixup` | 合并到上一个提交，丢弃这个的提交信息 | 同上，但不需要保留信息 |
| `reword` | 保留提交，但修改提交信息 | 写错了想改 |
| `drop` | 直接删除这个提交 | 完全不要这个提交 |

**举个例子：** 开发登录功能时产生了 3 个杂乱提交：

```
a1b2c3d feat: add login form
e4f5g6h fix typo
i7j8k9l wip: add button
```

在 rebase 编辑器中改为：

```
pick   a1b2c3d feat: add login form
squash e4f5g6h fix typo
squash i7j8k9l wip: add button
```

整理后变成一个干净的提交：

```
a1b2c3d feat: add login form with validation
```

**方法二：合并分支时用 squash merge**

把 feature 分支合并回 main 时，用 `--squash` 把所有提交压成一个：

```bash
git checkout main
git merge --squash feature/add-login
git commit -m "feat: add user login with validation and tests"
```

这样 main 上的历史永远是一条干净的线，每个提交都代表一个完整的功能。

**合并策略选择指南：**

| 你在做什么 | 用什么 | 为什么 |
|---|---|---|
| feature 合并回 main | `git merge --squash` | 一个功能 = 一个提交，历史干净 |
| 把 main 的更新同步到 feature | `git rebase main` | 保持线性历史，避免多余的 merge 提交 |
| 想完整保留开发过程 | `git merge`（不加参数） | 保留所有分支历史，适合需要审计的场景 |

---

## 第二部分：场景手册

> 以下是你日常最常遇到的 6 个场景，每个场景都给出了完整的操作步骤。

### 场景 1：开始开发一个新功能

```bash
# 1. 先同步 main 到最新
git checkout main
git pull

# 2. 创建功能分支（大功能才需要，小改动直接在 main 上做）
git checkout -b feature/add-dark-mode

# 3. 开发过程中小步提交
git add src/theme.ts
git commit -m "feat: add theme toggle component"

# 4. 开发完成，合并回 main
git checkout main
git merge --squash feature/add-dark-mode
git commit -m "feat: add dark mode support"

# 5. 删除分支
git branch -d feature/add-dark-mode
```

### 场景 2：开发到一半，需要紧急处理别的事

**为什么不能直接切分支？** 因为你当前有未提交的修改，直接切分支会把修改带过去，容易混乱。

**方案 A：用 stash 暂存（推荐，适合临时切换）**

`stash` 就是一个"临时存档"，把当前修改保存起来，工作区变干净，你可以自由切换。

```bash
git stash save "WIP: dashboard layout"    # 存档
git checkout main                          # 切走处理别的事
# ... 处理完了 ...
git checkout feature/dashboard             # 切回来
git stash pop                              # 读档，继续开发
```

**方案 B：直接提交 WIP（适合需要保留进度的长任务）**

```bash
git add .
git commit -m "wip: dashboard layout in progress"
# 切走去处理别的事，回来后继续开发
# 最后用 git rebase -i HEAD~N 把 WIP 提交整理干净
```

### 场景 3：发现了一个 Bug 要修

**如果你正在 feature 分支上开发：**

```bash
git stash                    # 先暂存当前工作
git checkout main            # 切到 main
# ... 修复 Bug ...
git add .
git commit -m "fix: resolve crash on null input"
git stash pop                # 恢复之前的工作，继续开发
```

**如果 Bug 很复杂，建议也开分支：**

```bash
git stash
git checkout -b fix/null-crash main
# ... 修复 ...
git checkout main
git merge --squash fix/null-crash
git commit -m "fix: resolve crash on null input"
git branch -d fix/null-crash
git stash pop
```

### 场景 4：想尝试一个不确定的方案

**为什么用 experiment 分支？** 因为如果方案不行，直接删分支就行，main 上不会留下任何痕迹。这比"改了再撤销"干净得多。

```bash
# 创建实验分支
git checkout -b experiment/try-redis-cache

# ... 尝试新方案 ...

# 方案好 → 合并到 main
git checkout main
git merge --squash experiment/try-redis-cache
git commit -m "feat: add redis caching layer"

# 方案不好 → 删掉分支，像什么都没发生过
git branch -D experiment/try-redis-cache
```

### 场景 5：想回退到之前的某个版本看看

```bash
# 只是看看代码，不想改任何东西
git checkout abc1234    # abc1234 是 commit hash（git log 能看到）
# ... 看看旧代码 ...
git checkout main       # 看完了，回到最新

# 想基于旧版本开新分支（比如在那个版本上修 Bug）
git checkout -b hotfix/old-version-fix abc1234
```

### 场景 6：想从其他分支挑一个特定的提交过来

**为什么用 cherry-pick 而不是 merge？** merge 会把整个分支的所有提交都合并过来，但你可能只需要其中某一个提交（比如一个 Bug 修复）。cherry-pick 就是"精准搬运"。

```bash
# 切到目标分支
git checkout main

# 搬一个提交过来
git cherry-pick abc1234

# 搬多个提交
git cherry-pick abc1234 def5678

# 搬过来但不自动提交（方便先审查代码）
git cherry-pick -n abc1234
```

---

## 第三部分：踩坑自救

> 出了问题别慌，Git 几乎所有操作都可以撤销。

### 撤销操作速查表

**这是最常用的救命表，建议收藏：**

| 你想做什么 | 命令 | 会丢代码吗？ |
|---|---|---|
| 撤销工作区的修改（还没 `git add`） | `git restore <file>` | ✅ 会丢，谨慎 |
| 取消暂存（已经 `git add`，还没 commit） | `git reset HEAD <file>` | ❌ 不会丢，代码还在 |
| 撤销最后一次提交，**保留**代码 | `git reset --soft HEAD~1` | ❌ 不会丢 |
| 撤销最后一次提交，**丢弃**代码 | `git reset --hard HEAD~1` | ✅ 会丢！谨慎！ |
| 安全撤销已推送的提交 | `git revert <commit-hash>` | ❌ 不会丢（创建新提交来反向操作） |
| 修改最后一次提交的信息 | `git commit --amend -m "新信息"` | ❌ 不会丢 |
| 给最后一次提交补充遗漏的文件 | `git add <file>` 然后 `git commit --amend --no-edit` | ❌ 不会丢 |

### 误删了分支

**能恢复吗？** 能！Git 有一个"操作录像"叫 reflog，记录了你做过的每一步操作。

```bash
git reflog
# 找到被删分支最后的那个 commit，比如：
# abc1234 HEAD@{3}: checkout: moving from my-branch to main

git checkout -b my-branch abc1234    # 用那个 commit 重建分支
```

### 误用了 `reset --hard`，代码没了

**别慌！** reflog 能找回 reset 之前的所有内容。

```bash
git reflog
# 找到 reset 之前的 commit，比如：
# abc1234 HEAD@{1}: commit: important work

git reset --hard abc1234    # 恢复到那个状态
```

### rebase 或 merge 搞乱了

**随时可以放弃，回到操作前的状态：**

```bash
git rebase --abort    # 放弃 rebase
git merge --abort     # 放弃 merge
```

### 合并冲突怎么解决？

**什么是冲突？** 两个分支修改了同一个文件的同一块区域，Git 不知道该保留哪个，需要你手动决定。

**冲突文件长这样：**

```
<<<<<<< HEAD
你当前分支的代码
=======
另一个分支的代码
>>>>>>> feature-branch
```

**解决步骤：**

```bash
git status              # 看哪些文件冲突了
# 用编辑器打开冲突文件，手动选择保留哪部分，删除 <<<< ==== >>> 标记
git add <file>          # 标记为已解决
git merge --continue    # 继续合并
# 如果搞不定，想放弃：git merge --abort
```

### 不小心把大文件 / 敏感信息 commit 进去了

**还没 push：** 直接撤销重来

```bash
git reset --soft HEAD~1    # 撤销提交，代码还在
# 删除大文件/敏感文件
git add .
git commit -m "fix: remove sensitive data"
```

**已经 push 了：** 用 filter-repo 从历史中彻底清除

```bash
git filter-repo --path big-file.zip --invert-paths --force
git gc --aggressive --prune=now
```

**预防：** 用 `.gitignore` 排除大文件，用 Git LFS 管理必须版本控制的大文件（如图片素材）。

### 定位"哪个提交引入了 Bug"（bisect）

**场景：** 你有 200 个提交，突然发现某个功能坏了，但不知道是哪次提交搞坏的。手动一个个看？太慢了。

**bisect 用二分法自动帮你定位：**

```bash
git bisect start
git bisect bad              # 当前版本有 Bug
git bisect good abc1234     # 这个版本没问题（找一个确定没问题的旧版本）

# Git 自动跳到中间的提交，你测试一下：
npm test
git bisect good             # 没问题 → Bug 在后面
# 或
git bisect bad              # 有问题 → Bug 在前面

# 重复 5-6 次后，Git 自动告诉你：
# first bad commit: abc1234 The problematic commit

git bisect reset            # 结束，回到原来的分支
```

甚至可以全自动：

```bash
git bisect start
git bisect bad
git bisect good abc1234
git bisect run npm test     # 自动运行测试，自动判断
git bisect reset
```

---

## 第四部分：配置优化

### 推荐全局配置（一劳永逸）

把以下配置写入你的全局 Git 配置，所有项目自动生效：

```bash
# 你的身份
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 新项目默认用 main 而不是 master
git config --global init.defaultBranch main

# pull 时自动 rebase，保持历史线性（避免产生多余的 merge 提交）
git config --global pull.rebase true

# 命令打错时自动纠正（比如 git stats → git status）
git config --global help.autocorrect 1

# 更智能的 diff 算法（处理代码移动时更清晰）
git config --global diff.algorithm histogram

# 彩色输出（更容易区分文件状态）
git config --global color.ui auto

# 你的编辑器（选一个你用的）
git config --global core.editor "code --wait"    # VS Code
git config --global core.editor "vim"             # Vim
```

### 实用别名（少打很多字）

```bash
git config --global alias.co checkout     # git co = git checkout
git config --global alias.br branch       # git br = git branch
git config --global alias.ci commit       # git ci = git commit
git config --global alias.st status       # git st = git status

git config --global alias.lg "log --oneline --graph --decorate --all"   # 美化的 log
git config --global alias.undo "reset --soft HEAD~1"                     # 撤销上次提交
git config --global alias.amend "commit --amend --no-edit"               # 补充文件到上次提交
git config --global alias.filelog "log --follow -p"                     # 查看文件修改历史
```

### 查看历史的实用命令

```bash
# 美观的图形化历史（最常用）
git log --oneline --graph --all --decorate

# 查看某个文件是怎么一步步变成现在的样子的
git log --follow -p src/utils/auth.ts

# 查看某次提交具体改了什么
git show <commit-hash>

# 搜索提交历史（按关键词）
git log --grep="login"

# 查看某行代码是谁写的、什么时候写的
git blame src/utils/auth.ts
git blame -L 10,20 src/utils/auth.ts    # 只看第 10-20 行
```

### 多工作区（worktree）

**为什么需要？** 有时候你需要同时开发两个功能，频繁切分支很烦（每次都要 stash 或 commit）。worktree 让你在同一个仓库里同时打开多个分支，各有各的文件夹，互不干扰。

```bash
# 为 feature 分支创建一个独立的工作区
git worktree add ../project-feature feature/dashboard

# 现在你有两个文件夹：
# ~/project/          → main 分支
# ~/project-feature/  → feature/dashboard 分支
# 可以同时打开两个编辑器窗口，各自开发！

# 完成后清理
git worktree remove ../project-feature
```

### 仓库性能维护

```bash
# 查看仓库占了多少空间
git count-objects -vH

# 垃圾回收（清理无用的历史数据，减小仓库体积）
git gc --aggressive --prune=now

# 在新电脑上克隆自己的大仓库时，只拉最近的内容
git clone --depth 1 <repo-url>
```

---

## 第五部分：仓库卫生与安全

### .gitignore——告诉 Git 哪些文件不要管

**为什么需要？** 依赖包（node_modules）、构建产物（dist/）、系统文件（.DS_Store）这些文件又大又容易变，没必要放进版本控制。更严重的是，敏感信息（密码、密钥）一旦提交就很难彻底清除。

**个人项目通用模板：**

```gitignore
# 依赖（别人能通过 package.json / requirements.txt 重新安装）
node_modules/
vendor/
.venv/

# 构建产物（能通过构建命令重新生成）
dist/
build/

# IDE 配置（每个人的设置不同）
.vscode/
.idea/

# 系统文件
.DS_Store
Thumbs.db

# 环境变量和密钥（绝对不能提交！）
.env
.env.local
*.pem
*.key

# 日志
*.log

# 大文件
*.zip
*.tar.gz
```

**已经提交过的文件怎么忽略？** `.gitignore` 只对"从未提交过"的文件生效。已经提交过的需要先从 Git 中移除：

```bash
git rm --cached <file>       # 从 Git 中移除，但保留本地文件
git rm -r --cached <dir>     # 移除整个目录
git commit -m "chore: remove tracked files from version control"
```

**全局 .gitignore（所有项目通用）：** 把 `.DS_Store`、IDE 配置等所有项目都一样的忽略规则放到全局文件里，不用每个项目都写一遍：

```bash
touch ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
```

### 安全红线

**绝对不要提交的内容：**

```
❌ 密码、API Key、Secret Key
❌ 数据库连接字符串
❌ 私钥文件（.pem, .key）
❌ .env 中的真实值
❌ 任何第三方服务的 Token
```

**正确做法：** 用 `.env.example` 作为模板（只写变量名，不写真实值），真实值放在 `.env` 里（已加入 .gitignore）：

```env
# .env.example（可以提交）
DATABASE_URL=your_database_url_here
API_KEY=your_api_key_here

# .env（不提交，包含真实值）
DATABASE_URL=postgresql://user:realpassword@localhost:5432/db
API_KEY=sk-abc123realkey456
```

**如果不小心提交了敏感信息：**

```
1. 立即轮换（重新生成）所有泄露的密钥 —— 这是最重要的一步！
2. 用 git filter-repo 从历史中清除
3. 强制推送
```

---

## 总结：个人项目 Git 的 4 个核心习惯

```
1. 提交前问自己："三个月后看到这条信息，我能明白做了什么吗？"
2. 每天结束前 commit 一次 —— 别丢了一天的进度
3. 每周清理一次已合并的分支 —— 保持仓库整洁
4. 敏感信息永远不进 Git —— 用 .env 管理
```

> **个人项目的 Git 规范不是为了给别人看，而是为了给三个月后的自己少挖坑。**
