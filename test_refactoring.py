#!/usr/bin/env python3
"""
AISocialEngine重构验证测试
验证所有适配器是否正确初始化和工作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_adapter_imports():
    """测试所有适配器是否可以正确导入"""
    print("=" * 60)
    print("测试1: 适配器导入测试")
    print("=" * 60)

    try:
        from backend.modules.sns.adapters import (
            UtilityAdapter,
            MessageProtocolAdapter,
            ResourceManagementAdapter,
            MovementAdapter,
            AgentCommunicationAdapter,
            PlaceSelectionAdapter,
            ToolManagementAdapter,
            PeopleCommunicationAdapter,
            XmppMessageAdapter,
            TradingAdapter,
            SkillServiceAdapter,
            TaskManagementAdapter,
            ActivityProcessingAdapter
        )
        print("✓ 所有13个适配器导入成功")
        return True
    except Exception as e:
        print(f"✗ 适配器导入失败: {e}")
        return False

def test_adapter_initialization():
    """测试适配器初始化"""
    print("\n" + "=" * 60)
    print("测试2: 适配器初始化测试")
    print("=" * 60)

    try:
        from backend.modules.sns.adapters import UtilityAdapter

        # 创建一个模拟的parent对象
        class MockParent:
            def __init__(self):
                self.aichatcfg_record = type('obj', (object,), {
                    'current_position': [116.0, 40.0],
                    'last_position': [116.0, 40.0]
                })()

        parent = MockParent()
        adapter = UtilityAdapter(parent)
        print("✓ UtilityAdapter初始化成功")

        # 测试一个简单的方法
        result = adapter.get_dict_by_id([{'id': '1', 'name': 'test'}], '1')
        if result and result['name'] == 'test':
            print("✓ UtilityAdapter.get_dict_by_id()方法工作正常")
        else:
            print("✗ UtilityAdapter.get_dict_by_id()方法返回错误")
            return False

        return True
    except Exception as e:
        print(f"✗ 适配器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_protocol_adapter():
    """测试协议适配器"""
    print("\n" + "=" * 60)
    print("测试3: 协议适配器功能测试")
    print("=" * 60)

    try:
        from backend.modules.sns.adapters import MessageProtocolAdapter

        class MockParent:
            pass

        parent = MockParent()
        adapter = MessageProtocolAdapter(parent)

        # 测试消息解析
        test_msg = "AISNS_INT_001_TOOL_DETAIL_SHOW_START{\"test\": \"data\"}AISNS_INT_001_TOOL_DETAIL_SHOW_END"
        result = adapter.get_tool_list_in_message(test_msg)

        if result == '{"test": "data"}':
            print("✓ MessageProtocolAdapter.get_tool_list_in_message()工作正常")
            return True
        else:
            print(f"✗ MessageProtocolAdapter返回错误: {result}")
            return False

    except Exception as e:
        print(f"✗ 协议适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 60)
    print("测试4: 文件结构验证")
    print("=" * 60)

    adapters_dir = "backend/modules/sns/adapters"
    expected_files = [
        "__init__.py",
        "utility_adapter.py",
        "message_protocol_adapter.py",
        "resource_management_adapter.py",
        "movement_adapter.py",
        "agent_communication_adapter.py",
        "place_selection_adapter.py",
        "tool_management_adapter.py",
        "people_communication_adapter.py",
        "xmpp_message_adapter.py",
        "trading_adapter.py",
        "skill_service_adapter.py",
        "task_management_adapter.py",
        "activity_processing_adapter.py"
    ]

    missing_files = []
    for filename in expected_files:
        filepath = os.path.join(adapters_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)

    if not missing_files:
        print(f"✓ 所有{len(expected_files)}个适配器文件都存在")
        return True
    else:
        print(f"✗ 缺少以下文件: {', '.join(missing_files)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("AISocialEngine重构验证测试")
    print("=" * 60 + "\n")

    results = []

    # 运行测试
    results.append(("文件结构验证", test_file_structure()))
    results.append(("适配器导入", test_adapter_imports()))
    results.append(("适配器初始化", test_adapter_initialization()))
    results.append(("协议适配器功能", test_protocol_adapter()))

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！重构成功！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
