"""
数据导出服务 - 支持Excel导出功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO
import pandas as pd
from fastapi import HTTPException


class ExcelExportService:
    """Excel导出服务"""
    
    @staticmethod
    def export_enterprise_list(data: List[Dict[str, Any]]) -> BytesIO:
        """
        导出企业列表到Excel
        
        Args:
            data: 企业数据列表
        
        Returns:
            Excel文件的字节流
        """
        if not data:
            raise HTTPException(status_code=400, detail="没有可导出的数据")
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 选择和重命名列
        column_mapping = {
            "enterprise_id": "企业ID",
            "enterprise_name": "企业名称",
            "organization_code": "组织机构代码",
            "enterprise_nature": "企业性质",
            "industry": "所属行业",
            "main_business": "主要经营业务",
            "contact_person": "联系人",
            "contact_address": "联系地址",
            "postal_code": "邮政编码",
            "contact_phone": "联系电话",
            "fax": "传真",
            "contact_email": "电子邮箱",
            "filing_status": "备案状态",
            "region_name": "所属地区",
            "created_at": "创建时间"
        }
        
        # 只保留存在的列
        available_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df_export = df[list(available_columns.keys())].copy()
        df_export.columns = list(available_columns.values())
        
        # 创建Excel写入器
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='企业列表', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['企业列表']
            
            # 自动调整列宽
            for idx, col in enumerate(df_export.columns, 1):
                max_length = max(
                    df_export[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_survey_data(data: List[Dict[str, Any]], survey_period_name: str = "") -> BytesIO:
        """
        导出调查数据到Excel
        
        Args:
            data: 调查数据列表
            survey_period_name: 调查期名称
        
        Returns:
            Excel文件的字节流
        """
        if not data:
            raise HTTPException(status_code=400, detail="没有可导出的数据")
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 选择和重命名列
        column_mapping = {
            "survey_id": "调查ID",
            "enterprise_id": "企业ID",
            "enterprise_name": "企业名称",
            "survey_period_id": "调查期ID",
            "report_month": "报告月份",
            "total_employees": "员工总数",
            "employed_count": "就业人数",
            "unemployed_count": "失业人数",
            "unemployment_rate": "失业率(%)",
            "new_employees": "新增就业",
            "lost_employees": "减少就业",
            "net_change": "净变化",
            "industry": "所属行业",
            "business_scale": "企业规模",
            "contact_person": "联系人",
            "contact_phone": "联系电话",
            "submit_time": "提交时间",
            "status": "状态"
        }
        
        # 只保留存在的列
        available_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df_export = df[list(available_columns.keys())].copy()
        df_export.columns = list(available_columns.values())
        
        # 格式化数值列
        numeric_columns = ["员工总数", "就业人数", "失业人数", "新增就业", "减少就业", "净变化"]
        for col in numeric_columns:
            if col in df_export.columns:
                df_export[col] = df_export[col].astype(int)
        
        # 格式化百分比列
        if "失业率(%)" in df_export.columns:
            df_export["失业率(%)"] = df_export["失业率(%)"].round(2)
        
        # 创建Excel写入器
        output = BytesIO()
        sheet_name = survey_period_name[:20] if survey_period_name else "调查数据"
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 获取工作表
            worksheet = writer.sheets[sheet_name]
            
            # 自动调整列宽
            for idx, col in enumerate(df_export.columns, 1):
                max_length = max(
                    df_export[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_summary_statistics(data: Dict[str, Any], survey_period_name: str = "") -> BytesIO:
        """
        导出汇总统计数据到Excel
        
        Args:
            data: 汇总统计数据
            survey_period_name: 调查期名称
        
        Returns:
            Excel文件的字节流
        """
        # 创建Excel写入器
        output = BytesIO()
        sheet_name = survey_period_name[:20] if survey_period_name else "汇总统计"
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 总体统计
            overall_stats = data.get("overall_statistics", {})
            if overall_stats:
                overall_df = pd.DataFrame([overall_stats])
                overall_df.columns = [f"总体统计 - {col}" for col in overall_df.columns]
                overall_df = overall_df.T
                overall_df.columns = ["数值"]
                overall_df.to_excel(writer, sheet_name='总体统计', header=True)
            
            # 维度统计
            dimension_stats = data.get("dimension_statistics", [])
            if dimension_stats:
                dimension_df = pd.DataFrame(dimension_stats)
                dimension_df.to_excel(writer, sheet_name='维度统计', index=False)
            
            # 时间序列数据
            time_series = data.get("time_series_data", [])
            if time_series:
                time_df = pd.DataFrame(time_series)
                time_df.to_excel(writer, sheet_name='时间序列', index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_audit_logs(data: List[Dict[str, Any]]) -> BytesIO:
        """
        导出审计日志到Excel
        
        Args:
            data: 审计日志列表
        
        Returns:
            Excel文件的字节流
        """
        if not data:
            raise HTTPException(status_code=400, detail="没有可导出的数据")
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 选择和重命名列
        column_mapping = {
            "log_id": "日志ID",
            "user_id": "用户ID",
            "username": "用户名",
            "operation": "操作类型",
            "resource_type": "资源类型",
            "resource_id": "资源ID",
            "details": "详细信息",
            "ip_address": "IP地址",
            "created_at": "操作时间"
        }
        
        # 只保留存在的列
        available_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df_export = df[list(available_columns.keys())].copy()
        df_export.columns = list(available_columns.values())
        
        # 创建Excel写入器
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='审计日志', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['审计日志']
            
            # 自动调整列宽
            for idx, col in enumerate(df_export.columns, 1):
                max_length = max(
                    df_export[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_notification_list(data: List[Dict[str, Any]]) -> BytesIO:
        """
        导出通知列表到Excel
        
        Args:
            data: 通知数据列表
        
        Returns:
            Excel文件的字节流
        """
        if not data:
            raise HTTPException(status_code=400, detail="没有可导出的数据")
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 选择和重命名列
        column_mapping = {
            "notification_id": "通知ID",
            "title": "通知标题",
            "content": "通知内容",
            "notification_type": "通知类型",
            "priority": "优先级",
            "sender_name": "发送者",
            "status": "状态",
            "distribution_progress": "分发进度(%)",
            "created_at": "创建时间",
            "published_at": "发布时间"
        }
        
        # 只保留存在的列
        available_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df_export = df[list(available_columns.keys())].copy()
        df_export.columns = list(available_columns.values())
        
        # 创建Excel写入器
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='通知列表', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['通知列表']
            
            # 自动调整列宽
            for idx, col in enumerate(df_export.columns, 1):
                max_length = max(
                    df_export[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def generate_filename(prefix: str, suffix: str = "xlsx") -> str:
        """
        生成导出文件名
        
        Args:
            prefix: 文件名前缀
            suffix: 文件后缀
        
        Returns:
            文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{suffix}"