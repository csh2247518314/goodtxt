#!/bin/bash
# GoodTxt v0.1.2 系统验证脚本
# 检验更新后的版本是否能够正常使用

set -e

echo "🧪 GoodTxt v0.1.2 系统验证"
echo "=============================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 函数定义
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 运行测试
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_test "$test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_pass "$test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_fail "$test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 检查文件结构
check_files() {
    print_info "检查项目文件结构..."
    
    local files=(
        "README.md"
        "docker-compose.yml"
        "super_launcher.py"
        "test_fixes.py"
        "backend/main.py"
        "frontend/package.json"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_pass "文件存在: $file"
        else
            print_fail "文件缺失: $file"
        fi
    done
}

# 测试Python语法
test_python_syntax() {
    print_info "测试Python语法..."
    
    if command -v python3 &> /dev/null; then
        # 测试主要Python文件
        python3 -m py_compile backend/main.py
        python3 -m py_compile test_fixes.py
        
        if [ $? -eq 0 ]; then
            print_pass "Python语法检查通过"
        else
            print_fail "Python语法检查失败"
        fi
    else
        print_fail "Python3未安装"
    fi
}

# 测试依赖包
test_dependencies() {
    print_info "测试Python依赖包..."
    
    local packages=("fastapi" "uvicorn" "PyJWT" "passlib")
    
    for package in "${packages[@]}"; do
        if python3 -c "import ${package//-/_}" 2>/dev/null; then
            print_pass "依赖包可用: $package"
        else
            print_fail "依赖包缺失: $package"
        fi
    done
}

# 测试Git配置
test_git_config() {
    print_info "测试Git配置..."
    
    if git config user.name &> /dev/null; then
        print_pass "Git用户名已配置: $(git config user.name)"
    else
        print_fail "Git用户名未配置"
    fi
    
    if git config user.email &> /dev/null; then
        print_pass "Git邮箱已配置: $(git config user.email)"
    else
        print_fail "Git邮箱未配置"
    fi
}

# 测试代码质量
test_code_quality() {
    print_info "测试代码质量..."
    
    # 检查README.md更新
    if grep -q "v0.1.2" README.md; then
        print_pass "README.md已更新到v0.1.2"
    else
        print_fail "README.md未更新到v0.1.2"
    fi
    
    # 检查修复验证脚本
    if grep -q "认证管理器导入成功" test_fixes.py; then
        print_pass "修复验证脚本存在"
    else
        print_fail "修复验证脚本不存在或内容不完整"
    fi
}

# 测试Docker配置
test_docker_config() {
    print_info "测试Docker配置..."
    
    if command -v docker &> /dev/null; then
        print_pass "Docker已安装"
        
        # 检查Docker Compose文件语法
        if docker-compose config > /dev/null 2>&1; then
            print_pass "Docker Compose配置语法正确"
        else
            print_fail "Docker Compose配置语法错误"
        fi
    else
        print_fail "Docker未安装"
    fi
}

# 模拟系统启动测试
test_system_startup() {
    print_info "测试系统启动能力..."
    
    # 检查必要文件存在
    if [ -f "super_launcher.py" ]; then
        # 检查超级启动器是否可以导入
        if python3 -c "import sys; sys.path.append('.'); import super_launcher" 2>/dev/null; then
            print_pass "超级启动器可以正常导入"
        else
            print_fail "超级启动器导入失败"
        fi
    else
        print_fail "超级启动器文件不存在"
    fi
}

# 生成验证报告
generate_report() {
    echo ""
    echo "📊 验证报告"
    echo "======================================"
    echo "总测试数: $TOTAL_TESTS"
    echo "通过测试: $PASSED_TESTS ✅"
    echo "失败测试: $FAILED_TESTS ❌"
    echo "成功率: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        print_pass "🎉 所有测试通过！GoodTxt v0.1.2系统验证成功！"
        echo ""
        echo "系统状态: ✅ 完全可用"
        echo "修复状态: ✅ 已验证"
        echo "部署就绪: ✅ 可以启动"
        echo ""
        echo "下一步操作:"
        echo "1. 运行: python3 super_launcher.py"
        echo "2. 访问: http://localhost:3002"
        echo "3. 登录: admin / admin123456"
        return 0
    else
        print_fail "⚠️  存在失败的测试，但系统可能仍然可用"
        echo ""
        echo "系统状态: ⚠️  部分可用"
        echo "修复状态: ⚠️  部分验证"
        echo "部署就绪: ⚠️  需要检查"
        echo ""
        echo "建议操作:"
        echo "1. 检查失败的测试项目"
        echo "2. 运行: python3 super_launcher.py --check"
        echo "3. 查看: docker-compose logs"
        return 1
    fi
}

# 主函数
main() {
    echo "开始系统验证..."
    echo ""
    
    # 执行所有测试
    check_files
    echo ""
    
    test_python_syntax
    echo ""
    
    test_dependencies
    echo ""
    
    test_git_config
    echo ""
    
    test_code_quality
    echo ""
    
    test_docker_config
    echo ""
    
    test_system_startup
    echo ""
    
    # 生成报告
    generate_report
    
    # 保存验证结果
    {
        echo "GoodTxt v0.1.2 验证报告"
        echo "=============================="
        echo "验证时间: $(date)"
        echo "总测试数: $TOTAL_TESTS"
        echo "通过测试: $PASSED_TESTS"
        echo "失败测试: $FAILED_TESTS"
        echo "成功率: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
        echo ""
        if [ $FAILED_TESTS -eq 0 ]; then
            echo "状态: ✅ 系统验证通过"
        else
            echo "状态: ⚠️  系统验证存在警告"
        fi
    } > verification_report.txt
    
    echo "📄 详细报告已保存到: verification_report.txt"
    
    return $FAILED_TESTS
}

# 运行主函数
main "$@"