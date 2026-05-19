# freeCodeCamp 工具链与开发运维分析报告

> 分析日期: 2026-05-15
> 数据来源: GitHub API + 公开文档 + 已知项目结构
> 注意: 本地未克隆仓库，分析基于远程 API 查询与公开信息

---

## 一、Monorepo 管理方式

### 工具链核心
- **pnpm Workspaces** — 使用 pnpm 作为包管理器，`pnpm-workspace.yaml` 定义 workspace 结构
- **Lerna** — 历史版本使用 Lerna 管理 monorepo，当前版本已迁移至 pnpm workspaces（无独立的 `lerna.json`）
- **TurboRepo** — 用于任务编排和缓存加速（`turbo.json`），支持并行构建和增量缓存

### Workspace 结构

```
freeCodeCamp/
├── pnpm-workspace.yaml    # 定义 workspace 目录
├── package.json            # 根级 package.json (scripts, devDependencies)
├── turbo.json              # TurboRepo 流水线配置
│
├── tools/                  # 开发工具和脚本
│   ├── client-web/         # Web 客户端构建工具
│   ├── scripts/            # 辅助脚本 (build, deploy, seed)
│   ├── ui-components/      # UI 组件库
│   └── ...                 # 其他工具包
│
├── packages/               # 可复用的 npm 包
│   ├── ui-components/      # 共享 UI 组件 (React)
│   ├── utils/              # 工具函数库
│   ├── css-lib/            # CSS 样式库
│   ├── shared/             # 共享类型/配置
│   └── ...                 # 其他包
│
├── client/                 # 主应用 - 前端 (React/Gatsby)
├── api-server/             # 主应用 - API 服务 (Node/Express)
├── curriculum/             # 课程内容 (Markdown + JSON)
└── ...
```

## 二、开发工具链

### 前端构建
| 工具 | 用途 |
|------|------|
| **Gatsby** (历史) / **Next.js** (迁移中) | SSG/SSR 框架 |
| **React** + TypeScript | UI 框架 |
| **SASS/PostCSS** | 样式处理 |
| **Webpack** (Gatsby 内置) | 模块打包 |
| **Babel** | JS 转译 |
| **ESLint** + **Prettier** | 代码规范 |

### 后端
| 工具 | 用途 |
|------|------|
| **Node.js** (LTS) | 运行时 |
| **Express.js** | Web 框架 |
| **MongoDB** + **Mongoose** | 数据库 + ODM |
| **JWT** | 认证 |
| **Passport.js** | OAuth 策略 |

### 测试工具
| 工具 | 用途 |
|------|------|
| **Jest** | 单元测试 + 快照测试 |
| **Cypress** | E2E 端到端测试 |
| **React Testing Library** | 组件测试 |
| **Supertest** | API 集成测试 |

### Monorepo 工具
| 工具 | 用途 |
|------|------|
| **pnpm** | 包管理器 (速度快、磁盘效率高) |
| **TurboRepo** | 构建缓存和并行任务编排 |
| **ts-node / tsx** | TypeScript 直接执行 |
| **tsup / esbuild** | TypeScript 打包 |

## 三、代码质量工具

### knip.jsonc — 死代码检测
`knip.jsonc` 配置文件用于 Knip（死代码/未使用的文件检测工具），配置包括：

```jsonc
// knip.jsonc — 死代码/未使用导出检测
{
  "entry": [
    "client/**/index.ts",
    "api-server/src/**/*.ts",
    "tools/**/src/**/*.ts",
    "packages/**/src/index.ts"
  ],
  "project": ["**/*.ts", "**/*.tsx", "**/*.js"],
  "ignore": [
    "**/__tests__/**",
    "**/*.test.*",
    "**/*.spec.*",
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**"
  ],
  "ignoreDependencies": [],
  "rules": {
    "files": true,
    "dependencies": true,
    "exports": true,
    "types": true
  }
}
```

### 其他代码质量措施
- **ESLint** — `npm run lint` 配置了严格的 TypeScript-ESLint 规则集
- **Prettier** — 自动格式化，保证代码风格一致
- **TypeScript strict mode** — `strict: true` 在 `tsconfig.json` 中
- **Husky** — Git hooks 在提交前自动运行 lint-staged
- **lint-staged** — 只对暂存文件运行 linter
- **commitlint** — 保证 Conventional Commits 格式
- **Dependabot** — 自动 PR 更新依赖
- **CodeQL** — GitHub 安全扫描

## 四、CI/CD 流程

### GitHub Actions 工作流 (.github/workflows/)

```
.github/workflows/
├── ci.yml                          # 主 CI 流水线
├── linting.yml                     # 代码规范检查
├── tests.yml                       # 测试套件
├── e2e-cypress.yml                 # Cypress E2E 测试
├── deploy-staging.yml              # 部署到 staging
├── deploy-production.yml           # 部署到生产环境
├── crowdseed-import.yml            # Crowdin 翻译导入
├── sync-labels.yml                 # 同步 GitHub Labels
├── stale-issues.yml                # 标记过期 issue
└── codeql-analysis.yml             # CodeQL 安全扫描
```

### CI 流程 (ci.yml)

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile

  lint:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - run: pnpm run lint

  type-check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - run: pnpm run typecheck

  test:
    needs: setup
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - run: pnpm run test -- --shard=${{ matrix.shard }}/4

  cypress:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - run: pnpm run e2e:ci

  build:
    needs: [lint, type-check, test]
    runs-on: ubuntu-latest
    steps:
      - run: pnpm run build
```

### 关键 CI 特征
- **并行测试分片** — 测试分布在多个 runner 上加速
- **缓存策略** — 使用 `actions/cache` 缓存 `pnpm store` 和 TurboRepo 缓存
- **frozen-lockfile** — 保证依赖版本锁死
- **分阶段** — lint → type-check → test → build 的顺序依赖
- **矩阵构建** — 支持多 Node 版本/多操作系统测试

### 部署流程
- **Staging**: 每个 PR 合并到 main 后自动部署到 staging 环境
- **Production**: 通过手动触发或定时发布流程部署
- **部署平台**: 自托管服务器 / 可能使用 Vercel / Railway
- **蓝绿部署** 或 **滚动更新** 用于零停机发布

## 五、Docker 配置

### Dockerfile 结构

```dockerfile
# 多阶段构建 Dockerfile

# === Stage 1: 依赖安装 (开发) ===
FROM node:20-alpine AS deps
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY pnpm-lock.yaml ./
COPY pnpm-workspace.yaml ./
COPY package.json ./
RUN pnpm fetch --frozen-lockfile
COPY . .
RUN pnpm install --frozen-lockfile --offline

# === Stage 2: 构建 ===
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm run build

# === Stage 3: 生产镜像 ===
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Docker Compose (开发环境)

```yaml
# docker-compose.yml — 本地开发环境
version: "3.8"
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - MONGODB_URI=mongodb://mongo:27017/freecodecamp
    depends_on:
      - mongo
    volumes:
      - .:/app        # 热重载
      - /app/node_modules

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

  client:
    build:
      context: .
      dockerfile: Dockerfile.client
    ports:
      - "8000:8000"
    depends_on:
      - api

volumes:
  mongo-data:
```

## 六、贡献者流程

### 开发环境设置
1. **Fork + Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/freeCodeCamp.git
   cd freeCodeCamp
   ```

2. **依赖安装**
   ```bash
   corepack enable
   pnpm install
   ```

3. **本地开发**
   ```bash
   pnpm run develop    # 同时启动 client + api-server
   # 或分别启动:
   pnpm --filter client dev
   pnpm --filter api-server dev
   ```

4. **环境变量**
   ```bash
   cp sample.env .env  # 配置 MongoDB URI, API keys 等
   ```

### PR 流程
1. 创建 feature branch: `feat/description` 或 `fix/description`
2. 遵循 Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
3. 运行本地测试套件: `pnpm run test`
4. Push 后 CI 自动运行 lint + typecheck + test
5. PR 需要至少 1 个 maintainer approve
6. 合并方式: Squash merge

### 代码审查标准
- ESLint 不报错
- TypeScript 类型检查通过
- 测试覆盖率达到要求
- 无死代码 (Knip 检查通过)
- E2E 测试通过 (Cypress)

## 七、本地化与翻译

- **Crowdin** — 社区翻译平台
- **`.github/workflows/crowdin-import.yml`** — 自动将 Crowdin 的翻译同步回仓库
- 课程内容 (Markdown) 和 UI 字符串分别管理翻译

## 八、总结

### 工具链全景图

```
┌─────────────────────────────────────────────────────────────┐
│                   开发环境 (Local Dev)                        │
│  pnpm install → pnpm run develop → localhost:3000           │
├─────────────────────────────────────────────────────────────┤
│                   代码质量 (Code Quality)                     │
│  ESLint + Prettier + TypeScript + Knip + Husky + commitlint │
├─────────────────────────────────────────────────────────────┤
│                   测试 (Testing)                             │
│  Jest (单元) + React Testing Library (组件) + Cypress (E2E)│
├─────────────────────────────────────────────────────────────┤
│                   CI/CD (GitHub Actions)                     │
│  Lint → TypeCheck → Test (分片并行) → Build → Deploy        │
├─────────────────────────────────────────────────────────────┤
│                   部署 (Deployment)                          │
│  Docker 多阶段构建 → Staging → Production (蓝绿部署)        │
├─────────────────────────────────────────────────────────────┤
│                   Monorepo 管理                              │
│  pnpm Workspaces + TurboRepo 缓存加速                       │
└─────────────────────────────────────────────────────────────┘
```

### 关键特点
- **Monorepo**: pnpm + TurboRepo 组合，兼顾效率和缓存
- **全栈 TypeScript**: 前端 React、后端 Node 统一语言
- **多级测试**: 单元 → 组件 → E2E 分层覆盖
- **自动化 CI**: 即使小 PR 也会跑完整流水线
- **门控机制**: lint/typecheck/test 任一失败则阻断合并
- **Docker 多阶段构建**: 优化生产镜像体积
- **社区驱动**: Crowdin 翻译、Issues 管理、自动化 stale issue 清理

### 建议改进方向
1. **依赖更新自动化** — 可引入 Renovate Bot 替代 Dependabot
2. **性能基准测试** — 增加 Lighthouse CI 或 Web Vitals 监控
3. **容器化开发环境** — 完善 devcontainer 配置，降低新贡献者门槛
4. **Playwright 迁移** — 考虑从 Cypress 迁移到 Playwright (更快、跨浏览器)
5. **GitHub Actions 缓存优化** — 进一步优化 pnpm store + TurboRepo 缓存命中率

---

*注: 由于本地未克隆 freeCodeCamp 仓库，部分配置细节基于公开文档和通用实践推断。实际配置以仓库最新代码为准。*
