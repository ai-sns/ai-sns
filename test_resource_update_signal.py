"""
测试资源更新信号和数据推送机制
验证 money、energy、life 等变化是否正确触发信号和更新前端
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_resource_updates():
    """测试资源更新机制"""
    from sqlalchemy.orm import Session
    from db.DBFactory import get_db
    from backend.modules.sns.ai_social_engine_adapter import AISocialEngine
    
    logger.info("=" * 60)
    logger.info("开始测试资源更新信号机制")
    logger.info("=" * 60)
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建 AISocialEngine 实例
        logger.info("\n1. 创建 AISocialEngine 实例...")
        engine = AISocialEngine(db)
        await engine.async_init()
        
        # 验证信号连接
        logger.info("\n2. 验证信号连接...")
        logger.info(f"   - aichatcfg_record 类型: {type(engine.aichatcfg_record)}")
        logger.info(f"   - 回调函数数量: {len(engine.aichatcfg_record._callbacks)}")
        logger.info(f"   - 已连接的回调: {engine.aichatcfg_record._callbacks}")
        
        # 检查 handle_aichatcfg_property_updated 是否已连接
        is_connected = engine.handle_aichatcfg_property_updated in engine.aichatcfg_record._callbacks
        logger.info(f"   - handle_aichatcfg_property_updated 已连接: {is_connected}")
        
        if not is_connected:
            logger.error("   ❌ 信号未正确连接！")
            return False
        else:
            logger.info("   ✅ 信号已正确连接")
        
        # 获取初始值
        logger.info("\n3. 获取初始资源值...")
        initial_money = engine.aichatcfg_record.money
        initial_life = engine.aichatcfg_record.life_point
        initial_energy = engine.aichatcfg_record.energy_point
        initial_move = engine.aichatcfg_record.move_point
        
        logger.info(f"   - 初始金钱: {initial_money}")
        logger.info(f"   - 初始生命值: {initial_life}")
        logger.info(f"   - 初始体力值: {initial_energy}")
        logger.info(f"   - 初始行动力: {initial_move}")
        
        # 测试 1: 直接修改 aichatcfg_record 属性
        logger.info("\n4. 测试直接修改 aichatcfg_record 属性...")
        logger.info("   - 修改 money...")
        engine.aichatcfg_record.money = initial_money + 100
        await asyncio.sleep(0.5)  # 等待信号处理
        
        logger.info("   - 修改 life_point...")
        engine.aichatcfg_record.life_point = max(0, initial_life - 10)
        await asyncio.sleep(0.5)
        
        logger.info("   - 修改 energy_point...")
        engine.aichatcfg_record.energy_point = max(0, initial_energy - 10)
        await asyncio.sleep(0.5)
        
        # 测试 2: 通过 ResourceManagementMixin 方法修改
        logger.info("\n5. 测试通过 ResourceManagementMixin 方法修改...")
        
        # 检查是否有 ResourceManagementMixin 的方法
        has_decline_life = hasattr(engine, 'decline_life')
        has_decline_energy = hasattr(engine, 'decline_energy')
        has_add_money = hasattr(engine, 'add_money')
        
        logger.info(f"   - 是否有 decline_life 方法: {has_decline_life}")
        logger.info(f"   - 是否有 decline_energy 方法: {has_decline_energy}")
        logger.info(f"   - 是否有 add_money 方法: {has_add_money}")
        
        if has_decline_life:
            logger.info("   - 调用 decline_life()...")
            engine.decline_life()
            await asyncio.sleep(0.5)
        
        if has_decline_energy:
            logger.info("   - 调用 decline_energy()...")
            engine.decline_energy()
            await asyncio.sleep(0.5)
        
        if has_add_money:
            logger.info("   - 调用 add_money(50)...")
            result = engine.add_money(50)
            logger.info(f"   - 返回结果: {result}")
            await asyncio.sleep(0.5)
        
        # 测试 3: 验证 update_map_charts 是否被调用
        logger.info("\n6. 测试 update_map_charts 调用...")
        
        # 手动调用 update_map_charts
        logger.info("   - 手动调用 update_map_charts()...")
        engine.update_map_charts()
        await asyncio.sleep(0.5)
        
        # 获取最终值
        logger.info("\n7. 获取最终资源值...")
        final_money = engine.aichatcfg_record.money
        final_life = engine.aichatcfg_record.life_point
        final_energy = engine.aichatcfg_record.energy_point
        final_move = engine.aichatcfg_record.move_point
        
        logger.info(f"   - 最终金钱: {final_money} (变化: {final_money - initial_money:+.2f})")
        logger.info(f"   - 最终生命值: {final_life} (变化: {final_life - initial_life:+d})")
        logger.info(f"   - 最终体力值: {final_energy} (变化: {final_energy - initial_energy:+d})")
        logger.info(f"   - 最终行动力: {final_move} (变化: {final_move - initial_move:+d})")
        
        # 测试 4: 检查 trade_mixin 中的资源变化
        logger.info("\n8. 检查 trade_mixin 中的资源变化方法...")
        
        # 检查是否有 set_food_order 方法
        has_set_food_order = hasattr(engine, 'set_food_order')
        logger.info(f"   - 是否有 set_food_order 方法: {has_set_food_order}")
        
        if has_set_food_order:
            logger.info("   - 调用 set_food_order()...")
            result = engine.set_food_order()
            logger.info(f"   - 返回结果: {result}")
            await asyncio.sleep(0.5)
            
            # 检查变化
            new_energy = engine.aichatcfg_record.energy_point
            new_money = engine.aichatcfg_record.money
            logger.info(f"   - 体力值变化: {final_energy} -> {new_energy}")
            logger.info(f"   - 金钱变化: {final_money} -> {new_money}")
        
        logger.info("\n" + "=" * 60)
        logger.info("测试完成！")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}", exc_info=True)
        return False
    finally:
        db.close()

async def test_signal_mechanism():
    """测试信号机制的详细流程"""
    from db.DBFactory import get_db
    from backend.modules.sns.ai_social_engine_adapter import AiChatCfgManager
    
    logger.info("\n" + "=" * 60)
    logger.info("测试 AiChatCfgManager 信号机制")
    logger.info("=" * 60)
    
    # 创建一个测试回调函数
    callback_called = []
    
    def test_callback(property_name):
        logger.info(f"   🔔 回调被触发！属性: {property_name}")
        callback_called.append(property_name)
    
    try:
        # 创建 AiChatCfgManager 实例
        logger.info("\n1. 创建 AiChatCfgManager 实例...")
        manager = AiChatCfgManager()
        
        # 连接回调
        logger.info("2. 连接测试回调...")
        manager.connect(test_callback)
        logger.info(f"   - 回调函数数量: {len(manager._callbacks)}")
        
        # 测试属性修改
        logger.info("\n3. 测试属性修改...")
        
        initial_money = manager.money
        logger.info(f"   - 初始金钱: {initial_money}")
        
        logger.info("   - 修改 money 属性...")
        manager.money = initial_money + 100
        await asyncio.sleep(0.1)
        
        logger.info(f"   - 新金钱值: {manager.money}")
        logger.info(f"   - 回调被调用次数: {len(callback_called)}")
        logger.info(f"   - 回调参数: {callback_called}")
        
        # 测试多个属性
        logger.info("\n4. 测试多个属性修改...")
        callback_called.clear()
        
        manager.life_point = 90
        await asyncio.sleep(0.1)
        
        manager.energy_point = 80
        await asyncio.sleep(0.1)
        
        manager.exp_point = 50
        await asyncio.sleep(0.1)
        
        logger.info(f"   - 回调被调用次数: {len(callback_called)}")
        logger.info(f"   - 回调参数: {callback_called}")
        
        # 验证结果
        logger.info("\n5. 验证结果...")
        expected_properties = ['money', 'life_point', 'energy_point', 'exp_point']
        success = all(prop in callback_called for prop in expected_properties)
        
        if success:
            logger.info("   ✅ 所有属性变化都触发了回调")
        else:
            logger.error("   ❌ 部分属性变化未触发回调")
            logger.error(f"   期望: {expected_properties}")
            logger.error(f"   实际: {callback_called}")
        
        return success
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("资源更新信号和数据推送测试")
    print("=" * 80)
    
    # 运行测试
    asyncio.run(test_signal_mechanism())
    asyncio.run(test_resource_updates())
