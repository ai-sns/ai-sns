import sys
import random
import string
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QDialog, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QDialogButtonBox, QRadioButton, QGroupBox, QLabel,
    QLineEdit, QGridLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from db.DBFactory import update_AiChatCfg_map
from i18n import lt
import re



class GeneralPage(QWidget):
    def __init__(self, task_record, parent=None):
        super(GeneralPage, self).__init__(parent)
        self.task_record = task_record
        self.parent = parent
        self.api_keys = None
        self.map_ids = None

        # Initialize UI components with task_record data
        self.initUI()

    def initUI(self):
        # Split the API keys and Map IDs
        api_keys = self.task_record.map_api_key.split(',') if self.task_record.map_api_key else ["", ""]
        map_ids = self.task_record.map_id.split(',') if self.task_record.map_id else ["", ""]

        self.api_keys = api_keys
        self.map_ids = map_ids


        # Google Map Group
        googleGroup = QGroupBox(lt("Google Map", "Google 地图"))
        self.mapApiKeyEdit = QLineEdit(api_keys[0])
        self.mapIdEdit = QLineEdit(map_ids[0])

        googleLayout = QGridLayout()
        googleLayout.addWidget(QLabel("地图API Key:"), 0, 0)
        googleLayout.addWidget(self.mapApiKeyEdit, 0, 1)
        googleLayout.addWidget(QLabel("地图ID:"), 1, 0)
        googleLayout.addWidget(self.mapIdEdit, 1, 1)
        googleGroup.setLayout(googleLayout)

        # Baidu Map Group
        baiduGroup = QGroupBox(lt("Baidu Map", "百度地图"))
        self.bdmapApiKeyEdit = QLineEdit(api_keys[1])
        self.bdmapIdEdit = QLineEdit(map_ids[1])

        baiduLayout = QGridLayout()
        baiduLayout.addWidget(QLabel("地图API Key:"), 0, 0)
        baiduLayout.addWidget(self.bdmapApiKeyEdit, 0, 1)
        baiduLayout.addWidget(QLabel("地图ID:"), 1, 0)
        baiduLayout.addWidget(self.bdmapIdEdit, 1, 1)
        baiduGroup.setLayout(baiduLayout)

        # Map Selection Group
        selectGroup = QGroupBox(lt("Select a map to use", "请选择使用的地图"))
        self.googleRadio = QRadioButton(lt("Google Map", "Google地图"))
        self.baiduRadio = QRadioButton(lt("Baidu Map", "百度地图"))

        if self.task_record.map_type == "1":
            self.baiduRadio.setChecked(True)
        else:
            self.googleRadio.setChecked(True)

        selectLayout = QGridLayout()
        selectLayout.addWidget(self.googleRadio, 0, 0)
        selectLayout.addWidget(self.baiduRadio, 0, 1)
        selectGroup.setLayout(selectLayout)

        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(googleGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(baiduGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(selectGroup)
        mainLayout.addSpacing(12)
        self.setLayout(mainLayout)
class ConfigDialog(QDialog):
    configured = pyqtSignal(str, str, str, str)
    connectcancel = pyqtSignal(str)

    def __init__(self, parent=None, task_record=None):
        super(ConfigDialog, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.resize(600, 100)
        self.task_record = task_record

        # Initialize the stack of pages
        self.initUI()

    def initUI(self):
        self.generalPage = GeneralPage(self.task_record, parent=self)
        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.generalPage)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.pagesWidget, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)

        button_box = self.createButtonBox()
        mainLayout.addWidget(button_box)

        self.setLayout(mainLayout)
        self.setWindowTitle(lt("Map Config", "地图设置"))
        self.map_selected = ""

    def createButtonBox(self):
        """Create a button box with OK and Cancel buttons."""
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText(lt("OK", "确定"))
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText(lt("Cancel", "取消"))
        button_box.accepted.connect(self.accept_close)
        button_box.rejected.connect(self.reject_close)
        return button_box

    def replace_in_file(self, filepath, replacements):
        """
        优化的文件内容替换函数 - 使用正则表达式精确定位替换位置

        Args:
            filepath: 文件路径
            replacements: 替换字典，格式: {old_value: new_value}

        Returns:
            bool: 替换是否成功
        """
        import os

        # 检查文件是否存在
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 - {filepath}")
            return False

        try:
            # 读取文件内容
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            replacement_count = 0

            # 根据文件类型确定替换策略
            for old_value, new_value in replacements.items():
                # 跳过无效值
                if not old_value or old_value == new_value or old_value == "N/A" or not new_value or new_value == "N/A":
                    continue

                # 根据文件类型使用不同的正则表达式模式
                patterns = []

                if 'googlemap' in filepath or 'google' in filepath:
                    # Google 地图相关文件的替换模式
                    # 1. HTML 中的 API Key: key=XXX
                    patterns.append((
                        r'(maps\.googleapis\.com/maps/api/js\?[^"\']*key=)' + re.escape(old_value),
                        r'\1' + new_value
                    ))
                    # 2. JavaScript 中的 mapId: "XXX"
                    patterns.append((
                        r'(mapId:\s*["\'])' + re.escape(old_value) + r'(["\'])',
                        r'\1' + new_value + r'\2'
                    ))

                elif 'map.html' in filepath or 'baidu' in filepath:
                    # 百度地图相关文件的替换模式
                    # 百度地图 API Key: ak=XXX
                    patterns.append((
                        r'(api\.map\.baidu\.com/api\?[^"\']*ak=)' + re.escape(old_value),
                        r'\1' + new_value
                    ))

                # 执行正则表达式替换
                for pattern, replacement in patterns:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        content = new_content
                        replacement_count += 1
                        print(f"  已替换: {old_value} -> {new_value}")

            # 如果没有任何替换，提示但不写入
            if replacement_count == 0:
                print(f"提示: {filepath} - 没有找到需要替换的内容")
                return True

            # 只有内容发生变化时才写入文件
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✓ 已处理: {filepath} (完成 {replacement_count} 处替换)")
                return True
            else:
                print(f"提示: {filepath} - 内容未变化")
                return True

        except Exception as e:
            print(f"✗ 错误: 处理文件 {filepath} 时发生异常 - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def accept_close(self):
        """Handle the acceptance of the dialog by validating inputs and updating the database."""
        import json

        # Retrieve and sanitize inputs, defaulting to "N/A" if empty
        google_api_key = self.generalPage.mapApiKeyEdit.text().strip() or "N/A"
        google_map_id = self.generalPage.mapIdEdit.text().strip() or "N/A"
        baidu_api_key = self.generalPage.bdmapApiKeyEdit.text().strip() or "N/A"
        baidu_map_id = self.generalPage.bdmapIdEdit.text().strip() or "N/A"

        # Validate selected map-related fields
        if self.generalPage.googleRadio.isChecked():
            self.map_selected = "google"
            # Google地图的API Key和地图ID都是必填的，且不能为N/A或空字符串
            if google_api_key == "N/A" or not google_api_key.strip():
                self.showError("Google地图的API Key为必填项，不能为空或N/A")
                return
            if google_map_id == "N/A" or not google_map_id.strip():
                self.showError("Google地图的地图ID为必填项，不能为空或N/A")
                return
            map_type = "0"  # Google selected
        else:
            self.map_selected = "baidu"
            # 百度地图的API Key是必填的
            if baidu_api_key == "N/A" or not baidu_api_key.strip():
                self.showError("百度地图的API Key为必填项，不能为空或N/A")
                return
            map_type = "1"  # Baidu selected

        # Check if map type is changing
        map_type_changing = (self.task_record.map_type != map_type)

        # Create comma-separated strings for API keys and map IDs
        map_api_key = f"{google_api_key},{baidu_api_key}"
        map_id = f"{google_map_id},{baidu_map_id}"

        # Prepare update parameters
        update_params = {
            "map_type": map_type,
            "map_api_key": map_api_key,
            "map_id": map_id
        }

        # If map type is changing, handle map position data
        if map_type_changing:
            # Load existing memo data
            memo_data = {}
            if self.task_record.memo:
                try:
                    memo_data = json.loads(self.task_record.memo)
                except json.JSONDecodeError:
                    memo_data = {}

            # Save current map position data to memo
            current_map_data = {
                "home_position": self.task_record.home_position,
                "positionx": self.task_record.positionx if self.task_record.positionx is not None else 0,
                "positiony": self.task_record.positiony if self.task_record.positiony is not None else 0,
                "positionz": self.task_record.positionz if self.task_record.positionz is not None else 0
            }

            if self.task_record.map_type == "0":  # Currently using Google
                memo_data["google"] = current_map_data
            elif self.task_record.map_type == "1":  # Currently using Baidu
                memo_data["baidu"] = current_map_data

            # Update memo field
            update_params["memo"] = json.dumps(memo_data, ensure_ascii=False)

            # Reset route fields
            update_params["route_start"] = ""
            update_params["route_end"] = ""
            update_params["route_current_position"] = ""
            update_params["route"] = ""
            update_params["route_status"] = "stopped"

            # Load map position data from memo for the new map type
            # If data doesn't exist for the target map, use current values as defaults
            if map_type == "0":  # Switching to Google
                if "google" in memo_data:  # Google data exists in memo
                    google_data = memo_data["google"]
                    update_params["home_position"] = google_data.get("home_position", self.task_record.home_position or "")
                    update_params["positionx"] = google_data.get("positionx", self.task_record.positionx or 0)
                    update_params["positiony"] = google_data.get("positiony", self.task_record.positiony or 0)
                    update_params["positionz"] = google_data.get("positionz", self.task_record.positionz or 0)
                else:  # No Google data in memo, use current values as defaults
                    update_params["home_position"] = self.task_record.home_position or ""
                    update_params["positionx"] = self.task_record.positionx or 0
                    update_params["positiony"] = self.task_record.positiony or 0
                    update_params["positionz"] = self.task_record.positionz or 0
            elif map_type == "1":  # Switching to Baidu
                if "baidu" in memo_data:  # Baidu data exists in memo
                    baidu_data = memo_data["baidu"]
                    update_params["home_position"] = baidu_data.get("home_position", self.task_record.home_position or "")
                    update_params["positionx"] = baidu_data.get("positionx", self.task_record.positionx or 0)
                    update_params["positiony"] = baidu_data.get("positiony", self.task_record.positiony or 0)
                    update_params["positionz"] = baidu_data.get("positionz", self.task_record.positionz or 0)
                else:  # No Baidu data in memo, use current values as defaults
                    update_params["home_position"] = self.task_record.home_position or ""
                    update_params["positionx"] = self.task_record.positionx or 0
                    update_params["positiony"] = self.task_record.positiony or 0
                    update_params["positionz"] = self.task_record.positionz or 0

        # Update the database with map details
        update_AiChatCfg_map(**update_params)

        # 获取原始值（用于替换）
        google_api_key_org = self.generalPage.api_keys[0] if len(self.generalPage.api_keys) > 0 else ""
        baidu_api_key_org = self.generalPage.api_keys[1] if len(self.generalPage.api_keys) > 1 else ""
        google_map_id_org = self.generalPage.map_ids[0] if len(self.generalPage.map_ids) > 0 else ""
        baidu_map_id_org = self.generalPage.map_ids[1] if len(self.generalPage.map_ids) > 1 else ""

        print("\n" + "="*60)
        print("开始替换地图配置文件中的 API Key 和 Map ID")
        print("="*60)

        # 处理 Google 地图相关文件
        if google_api_key != "N/A" or google_map_id != "N/A":
            google_replacements = {
                google_api_key_org: google_api_key,
                google_map_id_org: google_map_id,
            }

            print("\n[Google 地图配置]")
            print(f"  API Key: {google_api_key_org} -> {google_api_key}")
            print(f"  Map ID:  {google_map_id_org} -> {google_map_id}")

            # 替换 Google 地图 HTML 文件
            self.replace_in_file("scripts/googlemap3d.html", google_replacements)
            # 替换 Google 地图 JavaScript 文件
            self.replace_in_file("scripts/js/google/map_common.js", google_replacements)

        # 处理百度地图相关文件
        if baidu_api_key != "N/A":
            baidu_replacements = {
                baidu_api_key_org: baidu_api_key,
            }

            print("\n[百度地图配置]")
            print(f"  API Key: {baidu_api_key_org} -> {baidu_api_key}")

            # 替换百度地图 HTML 文件
            self.replace_in_file("scripts/map.html", baidu_replacements)
            # 如果有百度地图的 JS 文件，也可以在这里添加
            # self.replace_in_file("scripts/js/baidu/map_common.js", baidu_replacements)

        print("\n" + "="*60)
        print("地图配置文件替换完成")
        print("="*60 + "\n")

        self.accept()
        self.close()

    def reject_close(self):
        """Handle the rejection (closing without saving) of the dialog."""
        self.close()

    def showError(self, message):
        """Display an error message dialog."""
        errorDialog = QMessageBox(self)
        errorDialog.setIcon(QMessageBox.Icon.Warning)
        errorDialog.setWindowTitle("输入错误")
        errorDialog.setText(message)
        errorDialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = ConfigDialog(task_record=None)  # pass an actual task_record when available
    sys.exit(dialog.exec())
