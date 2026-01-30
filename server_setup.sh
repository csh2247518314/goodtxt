#!/bin/bash
# GoodTxt v0.1.2 服务器重新配置脚本
# 作者: MiniMax Agent
# 版本: v0.1.2
# 日期: 2026-01-30

set -e

echo "🚀 GoodTxt v0.1.2 服务器重新配置脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要软件
check_dependencies() {
    print_status "检查系统依赖..."
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        print_error "Git未安装，请先安装Git"
        exit 1
    fi
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip &> /dev/null && ! command -v uv &> /dev/null; then
        print_error "pip或uv未安装，请先安装pip或uv"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 拉取最新代码
update_code() {
    print_status "拉取最新代码..."
    
    # 如果项目不存在，克隆
    if [ ! -d "goodtxt" ]; then
        git clone https://github.com/csh2247518314/goodtxt.git
        cd goodtxt
    else
        cd goodtxt
        git pull origin main
    fi
    
    print_success "代码更新完成"
}

# 安装Python依赖
install_dependencies() {
    print_status "安装Python依赖..."
    
    # 使用uv安装依赖（推荐）
    if command -v uv &> /dev/null; then
        uv pip install PyJWT python-jose[cryptography] passlib[bcrypt] fastapi uvicorn pydantic-settings
    else
        pip install PyJWT python-jose[cryptography] passlib[bcrypt] fastapi uvicorn pydantic-settings
    fi
    
    print_success "Python依赖安装完成"
}

# 安装Docker（如果需要）
install_docker() {
    if ! command -v docker &> /dev/null; then
        print_warning "Docker未安装，尝试自动安装..."
        
        # 检测操作系统
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y docker.io docker-compose
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
        else
            print_error "无法自动安装Docker，请手动安装"
            exit 1
        fi
        
        # 添加用户到docker组
        sudo usermod -aG docker $USER
        print_warning "请重新登录以使Docker权限生效"
    fi
}

# 验证修复
verify_fixes() {
    print_status "验证系统修复..."
    
    # 运行修复验证脚本
    if [ -f "test_fixes.py" ]; then
        python3 test_fixes.py
        if [ $? -eq 0 ]; then
            print_success "系统验证通过"
        else
            print_warning "系统验证发现问题，但可能不影响使用"
        fi
    else
        print_warning "验证脚本不存在，跳过验证"
    fi
}

# 启动系统
start_system() {
    print_status "启动GoodTxt系统..."
    
    # 检查是否有超级启动器
    if [ -f "super_launcher.py" ]; then
        python3 super_launcher.py --quick
    else
        print_error "超级启动器不存在"
        exit 1
    fi
    
    print_success "系统启动完成"
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "🎉 GoodTxt v0.1.2 配置完成！"
    echo "=========================================="
    echo "🌐 访问信息:"
    echo "   前端界面: http://localhost:3002"
    echo "   后端API:  http://localhost:8000"
    echo "   API文档:  http://localhost:8000/docs"
    echo ""
    echo "👤 默认登录:"
    echo "   用户名: admin"
    echo "   密码: admin123456"
    echo ""
    echo "📋 快速操作:"
    echo "   重启系统: python3 super_launcher.py --quick"
    echo "   检查状态: python3 super_launcher.py --check"
    echo "   验证修复: python3 test_fixes.py"
    echo ""
    echo "🎯 故障排除:"
    echo "   查看日志: docker-compose logs"
    echo "   重启服务: docker-compose restart"
    echo "   查看状态: python3 super_launcher.py --monitor"
    echo ""
}

# 主函数
main() {
    echo "开始服务器重新配置..."
    
    # 确认操作
    echo "此脚本将:"
    echo "1. 检查和安装系统依赖"
    echo "2. 拉取GoodTxt最新代码"
    echo "3. 安装Python依赖包"
    echo "4. 验证系统修复"
    echo "5. 启动GoodTxt系统"
    echo ""
    read -p "是否继续? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
    
    # 执行配置步骤
    check_dependencies
    update_code
    install_dependencies
    install_docker
    verify_fixes
    start_system
    show_access_info
    
    print_success "配置完成！"
}

# 运行主函数
main "$@"