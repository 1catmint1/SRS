# Git仓库配置和提交指南

## 📋 当前Git状态

### 已创建的分支
- **master**: 主分支，用于生产环境
- **v0.5-alpha**: v0.5 Alpha版本的稳定分支
- **develop**: 开发分支，用于日常开发工作

### 当前分支
```
* develop (当前所在分支)
  master
  v0.5-alpha
```

---

## 🚀 推送到远程仓库

### 步骤1: 创建远程仓库
在Git托管平台(如GitHub、GitLab、Gitee等)创建一个新的空仓库。

### 步骤2: 添加远程仓库地址
```bash
# 替换为您的远程仓库地址
git remote add origin https://github.com/your-username/SRS.git

# 或者使用SSH地址
git remote add origin git@github.com:your-username/SRS.git
```

### 步骤3: 推送所有分支到远程仓库
```bash
# 推送master分支
git push -u origin master

# 推送v0.5-alpha分支
git push -u origin v0.5-alpha

# 推送develop分支
git push -u origin develop
```

### 步骤4: 设置默认推送分支
```bash
# 设置master为默认推送分支
git push -u origin master

# 或者设置develop为默认推送分支
git push -u origin develop
```

---

## 🌿 分支管理策略

### 分支说明
1. **master分支**: 生产环境分支，保持稳定
2. **v0.5-alpha分支**: 当前版本的稳定分支，用于bug修复
3. **develop分支**: 开发分支，用于新功能开发

### 分支切换
```bash
# 切换到master分支
git checkout master

# 切换到v0.5-alpha分支
git checkout v0.5-alpha

# 切换到develop分支
git checkout develop
```

### 创建新分支
```bash
# 从develop创建新功能分支
git checkout develop
git checkout -b feature/new-feature

# 从v0.5-alpha创建修复分支
git checkout v0.5-alpha
git checkout -b hotfix/bug-fix
```

---

## 📝 日常开发流程

### 1. 在develop分支开发新功能
```bash
git checkout develop
git pull origin develop
# 进行代码修改...
git add .
git commit -m "描述您的修改"
git push origin develop
```

### 2. 修复v0.5-alpha分支的bug
```bash
git checkout v0.5-alpha
git pull origin v0.5-alpha
# 进行bug修复...
git add .
git commit -m "修复: 描述bug修复内容"
git push origin v0.5-alpha
```

### 3. 合并分支
```bash
# 将develop合并到master
git checkout master
git merge develop
git push origin master

# 将hotfix合并到master和develop
git checkout master
git merge hotfix/bug-fix
git push origin master

git checkout develop
git merge hotfix/bug-fix
git push origin develop
```

---

## 🔍 常用Git命令

### 查看状态
```bash
git status              # 查看工作区状态
git branch              # 查看本地分支
git branch -a           # 查看所有分支(包括远程)
git log                 # 查看提交历史
git log --oneline       # 查看简洁的提交历史
```

### 查看差异
```bash
git diff                # 查看工作区与暂存区的差异
git diff --staged       # 查看暂存区与上次提交的差异
git diff branch1 branch2  # 比较两个分支的差异
```

### 撤销操作
```bash
git checkout -- file    # 撤销工作区的修改
git reset HEAD file     # 取消暂存区的修改
git reset --soft HEAD~1 # 撤销最后一次提交，保留修改
git reset --hard HEAD~1 # 撤销最后一次提交，不保留修改
```

### 远程操作
```bash
git remote -v           # 查看远程仓库
git remote add origin url  # 添加远程仓库
git remote remove origin  # 删除远程仓库
git fetch origin        # 获取远程仓库的最新信息
git pull origin master  # 拉取远程分支并合并
git push origin master  # 推送到远程分支
```

---

## 📊 项目版本规划

### 当前版本: v0.5 Alpha
- **分支**: v0.5-alpha
- **状态**: 稳定版本
- **功能**: JWT认证、RBAC权限、企业备案审批、系统管理

### 计划版本: v0.8 Beta
- **分支**: 待创建
- **计划功能**: 市级初审、省市级终审、数据统计分析

### 未来版本: v1.0 GA
- **分支**: 待创建
- **计划功能**: 完整的三级流转、趋势预测、国家系统对接

---

## 🎯 提交消息规范

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型
- **feat**: 新功能
- **fix**: Bug修复
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建/工具链相关

### 示例
```bash
feat(auth): 添加用户信息查询接口
fix(admin): 修复调查期日期验证错误
docs(readme): 更新安装说明
```

---

## 🚨 注意事项

1. **不要提交敏感信息**: 
   - 密码
   - API密钥
   - 个人信息

2. **不要提交大文件**:
   - 虚拟环境文件
   - 编译产物
   - 临时文件

3. **定期提交**: 
   - 完成一个功能就提交
   - 提交前先pull
   - 写清楚提交消息

4. **分支管理**:
   - 不要直接在master分支开发
   - 使用feature分支开发新功能
   - 使用hotfix分支修复bug

---

## 📞 获取帮助

### Git官方文档
- https://git-scm.com/doc

### 常用平台
- GitHub: https://github.com
- GitLab: https://gitlab.com
- Gitee: https://gitee.com

### 图形化工具
- SourceTree
- GitKraken
- GitHub Desktop

---

**创建时间**: 2026年3月30日  
**当前版本**: v0.5 Alpha  
**Git状态**: ✅ 仓库已初始化，分支已创建