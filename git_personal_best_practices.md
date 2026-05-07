# 个人项目 Git 规范指南

> 单人项目也要有 Git 纪律。清晰的提交历史就是你的开发日记。

## 速查：你应该看哪部分？

| 你现在想做什么 | 直接跳到 |
|---|---|
| 提交信息不知道怎么写 | [基础规范 - 提交信息](#11-提交信息怎么写) |
| 分支什么时候该建、怎么命名 | [基础规范 - 分支怎么用](#13-分支怎么用) |
| 提交历史很乱，想整理 | [基础规范 - 保持历史整洁](#14-保持历史整洁) |
| 遇到了问题想救命 | [踩坑自救 - 撤销速查表](#31-撤销操作速查表) |
| 想改写已推送的提交信息 | [场景 5：批量改写已推送的提交信息](#场景-5批量改写已推送的提交信息) |
| 想让 Git 更顺手 | [配置优化](#四配置优化) |

---

## 一、基础规范

### 1.1 提交信息怎么写

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
| `ci` | CI/CD 配置变更 | `ci: add GitHub Pages deployment workflow` |

**三条铁律：**

1. **说清楚做了什么** -- `fix: resolve crash on empty input` 合格 vs `fix bug` 不合格
2. **用祈使句、现在时** -- `add feature` 合格 vs `added feature` 不合格
3. **一行不超过 72 字符** -- 太长在终端里会换行

**复杂变更可以写多行：**

```
feat: add order export to CSV

- Implement CSV generation with proper escaping
- Add date range filter for export
- Support both simplified and traditional Chinese headers

This allows shop owners to export order data for
accounting purposes, which was the #1 requested feature.
```

### 1.2 提交粒度：一次提交该包含多少？

**原则：一个提交 = 一个逻辑变更。**

```
合格做法：一次提交只做一件事（加登录功能、修一个 Bug、更新一段文档）
不合格做法：一次提交包含（登录功能 + 修 Bug + 更新依赖 + 格式调整）
```

**实际操作：**

```bash
# 合格：按功能分批
git add src/auth/login.ts
git commit -m "feat: add login form validation"

git add src/auth/register.ts
git commit -m "feat: add registration form"

git add tests/auth.test.ts
git commit -m "test: add unit tests for auth module"
```

### 1.3 分支怎么用

单人项目的分支策略非常简单：`main` 始终是"能跑的版本"。

**什么时候需要建分支？**

| 场景 | 建议 |
|---|---|
| 改个错别字、调个样式 | 直接在 main 上提交就行 |
| 尝试一个不确定的新方案 | 建分支，不行就删 |
| 需要开发几天的大功能 | 建分支，完成后合并 |
| 修一个复杂的 Bug | 建分支，避免和功能开发混在一起 |

**分支命名格式：`类型/简短描述`**

```
feature/add-dark-mode       -- 新功能
experiment/try-redis-cache  -- 实验性尝试
fix/login-timeout           -- Bug 修复
chore/update-deps           -- 杂务
```

**用完就删：**

```bash
git branch -d feature/add-dark-mode    # 合并后删除
git branch --merged                     # 查看哪些已合并
```

### 1.4 保持历史整洁

**方法一：提交前用交互式 rebase 整理**

```bash
git rebase -i HEAD~3    # 整理最近 3 个提交
```

在编辑器中对每个提交选择操作：

| 操作 | 效果 | 什么时候用 |
|---|---|---|
| `pick` | 保留这个提交 | 默认 |
| `squash` | 合并到上一个提交，保留两个的提交信息 | 把"修 typo"合并到"加功能"里 |
| `fixup` | 合并到上一个提交，丢弃这个的提交信息 | 同上，但不需要保留信息 |
| `reword` | 保留提交，但修改提交信息 | 写错了想改 |
| `drop` | 直接删除这个提交 | 完全不要这个提交 |

**方法二：合并分支时用 squash merge**

```bash
git checkout main
git merge --squash feature/add-login
git commit -m "feat: add user login with validation and tests"
```

**合并策略选择：**

| 你在做什么 | 用什么 | 为什么 |
|---|---|---|
| feature 合并回 main | `git merge --squash` | 一个功能 = 一个提交，历史干净 |
| 把 main 的更新同步到 feature | `git rebase main` | 保持线性历史 |
| 想完整保留开发过程 | `git merge`（不加参数） | 保留所有分支历史 |

### 1.5 个人项目 4 个核心习惯

1. 提交前问自己："三个月后看到这条信息，我能明白做了什么吗？"
2. 每天结束前 commit 一次 -- 别丢了一天的进度
3. 每周清理一次已合并的分支 -- 保持仓库整洁
4. 敏感信息永远不进 Git -- 用 .env 管理

---

## 二、场景手册

> 以下是你日常最常遇到的 7 个场景。

### 场景 1：开始开发一个新功能

```bash
# 1. 先同步 main 到最新
git checkout main
git pull

# 2. 创建功能分支（大功能才需要）
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

**方案 A：用 stash 暂存（推荐，适合临时切换）**

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

```bash
git stash                    # 先暂存当前工作
git checkout main            # 切到 main
# ... 修复 Bug ...
git add .
git commit -m "fix: resolve crash on null input"
git stash pop                # 恢复之前的工作
```

### 场景 4：想尝试一个不确定的方案

```bash
# 创建实验分支
git checkout -b experiment/try-redis-cache

# ... 尝试新方案 ...

# 方案好 -> 合并到 main
git checkout main
git merge --squash experiment/try-redis-cache
git commit -m "feat: add redis caching layer"

# 方案不好 -> 删掉分支
git branch -D experiment/try-redis-cache
```

### 场景 5：批量改写已推送的提交信息

> 适用于已提交但未推送、或单人项目中已推送需要改 message 的情况。

**核心原理：** `git filter-branch --msg-filter` 逐条将每个 commit 的 message 通过管道传给一个外部脚本，脚本读入旧信息、输出新信息。

**1. 写一个 msg-filter 脚本**

```python
# msg_filter.py -- 放在项目根目录
import sys
old = sys.stdin.buffer.read().decode("utf-8").strip()
rewrites = {
    "旧信息1": "新信息1",
    "旧信息2": "新信息2",
}
sys.stdout.write(rewrites.get(old, old) + "\n")
```

**2. 执行 filter-branch**

```bash
# 用绝对路径调用脚本（filter-branch 会在临时目录下运行）
# 示例（Windows）：git filter-branch --msg-filter "python D:/项目/path/to/msg_filter.py" -- --all
# 示例（Linux/Mac）：git filter-branch --msg-filter "python /home/user/project/msg_filter.py" -- --all
git filter-branch --msg-filter "python /absolute/path/to/msg_filter.py" -- --all
```

**3. 清理备份 ref**

```bash
git update-ref -d refs/original/refs/heads/main
```

**4. 确认历史正确后 force push**

```bash
git push --force origin main
```

**注意事项：**

| 注意点 | 说明 |
|---|---|
| 脚本路径要用**绝对路径** | filter-branch 在 `.git-rewrite/` 临时目录下执行，相对路径找不到 |
| `-- --all` 处理所有分支 | 确保所有远程分支都同步 |
| 每个 commit 的 hash 都会变 | 新建 commit 替换旧 commit |
| 作者日期（AuthorDate）**保留** | GitHub 显示不变 |
| **需要 force push** | 改写历史后必须用 `--force` 覆盖远程 |
| 仅单人项目使用 | 多人项目改写已推送的历史会导致协作混乱 |

### 场景 6：想回退到之前的某个版本看看

```bash
# 只是看看代码
git checkout abc1234    # abc1234 是 commit hash
# ... 看看旧代码 ...
git checkout main       # 回到最新

# 想基于旧版本开新分支
git checkout -b hotfix/old-version-fix abc1234
```

### 场景 7：想从其他分支挑一个特定的提交过来

```bash
# cherry-pick = 精准搬运，不合并整个分支
git checkout main
git cherry-pick abc1234           # 搬一个
git cherry-pick abc1234 def5678   # 搬多个
git cherry-pick -n abc1234        # 搬过来但不自动提交（先审查代码）
```

---

## 三、踩坑自救

> 出了问题别慌，Git 几乎所有操作都可以撤销。

### 3.1 撤销操作速查表

| 你想做什么 | 命令 | 会丢代码吗？ |
|---|---|---|
| 撤销工作区的修改（还没 `git add`） | `git restore <file>` | 会丢，谨慎 |
| 取消暂存（已经 `git add`，还没 commit） | `git reset HEAD <file>` | 不会丢 |
| 撤销最后一次提交，**保留**代码 | `git reset --soft HEAD~1` | 不会丢 |
| 撤销最后一次提交，**丢弃**代码 | `git reset --hard HEAD~1` | 会丢！谨慎！ |
| 安全撤销已推送的提交 | `git revert <commit-hash>` | 不会丢（创建新提交反向操作） |
| 修改最后一次提交的信息 | `git commit --amend -m "新信息"` | 不会丢 |
| 给最后一次提交补充遗漏的文件 | `git add <file>` + `git commit --amend --no-edit` | 不会丢 |

### 3.2 误删了分支 / 误用 reset --hard

```bash
# 用 reflog 找回（reflog 记录了你做过的每一步操作）
git reflog
# 找到被删分支最后的 commit，比如：
# abc1234 HEAD@{3}: checkout: moving from my-branch to main

git checkout -b my-branch abc1234    # 用那个 commit 重建分支
git reset --hard abc1234             # 恢复到那个状态
```

### 3.3 rebase 或 merge 搞乱了

```bash
git rebase --abort    # 放弃 rebase
git merge --abort     # 放弃 merge
```

### 3.4 合并冲突怎么解决？

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
# 用编辑器打开冲突文件，手动选择保留哪部分，删除 <<<< ==== >>>> 标记
git add <file>          # 标记为已解决
git merge --continue    # 继续合并
# 如果搞不定：git merge --abort
```

### 3.5 不小心把大文件 / 敏感信息 commit 进去了

**还没 push：**

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

**预防：** 用 `.gitignore` 排除大文件，用 Git LFS 管理必须版本控制的大文件。

### 3.6 定位哪个提交引入了 Bug（bisect）

```bash
git bisect start
git bisect bad              # 当前版本有 Bug
git bisect good abc1234     # 这个版本没问题
# Git 自动跳到中间的提交，你测试一下
npm test
git bisect good             # 没问题 -> Bug 在后面
# 或
git bisect bad              # 有问题 -> Bug 在前面
# 重复 5-6 次后，Git 自动告诉你
# first bad commit: abc1234 The problematic commit
git bisect reset            # 结束
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

## 四、配置优化

### 4.1 推荐全局配置

```bash
# 你的身份
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 新项目默认用 main
git config --global init.defaultBranch main

# pull 时自动 rebase，保持历史线性
git config --global pull.rebase true

# 命令打错时自动纠正
git config --global help.autocorrect 1

# 更智能的 diff 算法
git config --global diff.algorithm histogram

# 彩色输出
git config --global color.ui auto

# 你的编辑器
git config --global core.editor "code --wait"
```

### 4.2 实用别名

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.undo "reset --soft HEAD~1"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.filelog "log --follow -p"
```

### 4.3 查看历史的实用命令

```bash
# 美观的图形化历史
git log --oneline --graph --all --decorate

# 查看某个文件的完整修改历史
git log --follow -p src/utils/auth.ts

# 查看某次提交具体改了什么
git show <commit-hash>

# 搜索提交历史
git log --grep="login"

# 查看某行代码是谁写的
git blame src/utils/auth.ts
git blame -L 10,20 src/utils/auth.ts    # 只看第 10-20 行
```

### 4.4 多工作区（worktree）

```bash
# 为 feature 分支创建一个独立的工作区
git worktree add ../project-feature feature/dashboard

# 现在你有两个文件夹，可以同时开发
# ../project/          -> main 分支
# ../project-feature/  -> feature/dashboard 分支

# 完成后清理
git worktree remove ../project-feature
```

### 4.5 仓库性能维护

```bash
git count-objects -vH                        # 查看仓库占了多少空间
git gc --aggressive --prune=now              # 垃圾回收
git clone --depth 1 <repo-url>               # 只拉最近的内容
```

---

## 五、仓库卫生与安全

### 5.1 .gitignore

**个人项目通用模板：**

```gitignore
# 依赖
node_modules/
vendor/
.venv/

# 构建产物
dist/
build/

# IDE 配置
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

**已经提交过的文件怎么忽略？** `.gitignore` 只对从未提交过的文件生效。

```bash
git rm --cached <file>       # 从 Git 中移除，但保留本地文件
git rm -r --cached <dir>     # 移除整个目录
git commit -m "chore: remove tracked files from version control"
```

**全局 .gitignore：** 把 `.DS_Store`、IDE 配置等通用规则放到全局文件。

```bash
touch ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
```

### 5.2 安全红线

**绝对不要提交的内容：**

- 密码、API Key、Secret Key
- 数据库连接字符串
- 私钥文件（.pem, .key）
- .env 中的真实值
- 任何第三方服务的 Token

**正确做法：** 用 `.env.example` 作为模板（只写变量名，不写真实值），真实值放在 `.env` 里（已加入 .gitignore）。

```env
# .env.example（可以提交）
DATABASE_URL=your_database_url_here
API_KEY=your_api_key_here
```

**如果不小心提交了敏感信息：**

1. 立即轮换（重新生成）所有泄露的密钥 -- 这是最重要的一步！
2. 用 git filter-repo 从历史中清除
3. 强制推送

---

> **个人项目的 Git 规范不是为了给别人看，而是为了给三个月后的自己少挖坑。**
