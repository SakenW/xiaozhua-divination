#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六爻纳甲排盘工具 v2.0.0
天工长老开发

功能：六爻起卦、纳甲、装卦、六亲、世应、六神排布、动爻变卦、自动化断卦
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# ============== 基础数据 ==============

# 八卦
BA_GUA = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

# 八卦二进制表示（从初爻到上爻，即从低位到高位；1=阳 0=阴）
# 乾☰=111 兑☱=110 离☲=101 震☳=100 巽☴=011 坎☵=010 艮☶=001 坤☷=000
# 先天卦序：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8
GUA_BINARY = {
    '乾': (1, 1, 1), '兑': (1, 1, 0), '离': (1, 0, 1), '震': (1, 0, 0),
    '巽': (0, 1, 1), '坎': (0, 1, 0), '艮': (0, 0, 1), '坤': (0, 0, 0),
}
# 反查表：二进制 tuple → 先天卦序编号（1-8）
BINARY_TO_GUA_IDX = {v: i + 1 for i, v in enumerate(
    [GUA_BINARY[g] for g in BA_GUA]
)}

# 八卦纳甲（每卦从初爻到上爻的纳干）
NA_JIA_GAN = {
    '乾': ['甲', '甲', '甲', '壬', '壬', '壬'],  # 乾卦内卦纳甲，外卦纳壬
    '坤': ['乙', '乙', '乙', '癸', '癸', '癸'],  # 坤卦内卦纳乙，外卦纳癸
    '震': ['庚', '庚', '庚', '庚', '庚', '庚'],
    '巽': ['辛', '辛', '辛', '辛', '辛', '辛'],
    '坎': ['戊', '戊', '戊', '戊', '戊', '戊'],
    '离': ['己', '己', '己', '己', '己', '己'],
    '艮': ['丙', '丙', '丙', '丙', '丙', '丙'],
    '兑': ['丁', '丁', '丁', '丁', '丁', '丁'],
}

# 八卦五行
BA_GUA_WUXING = {
    '乾': '金', '兑': '金', '离': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土'
}

# 六十四卦名（上卦 + 下卦）
LIU_SHI_SI_GUA = {
    '乾乾': '乾为天', '乾兑': '天泽履', '乾离': '天火同人', '乾震': '天雷无妄',
    '乾巽': '天风姤', '乾坎': '天水讼', '乾艮': '天山遁', '乾坤': '天地否',
    '兑乾': '泽天夬', '兑兑': '兑为泽', '兑离': '泽火革', '兑震': '泽雷随',
    '兑巽': '泽风大过', '兑坎': '泽水困', '兑艮': '泽山咸', '兑坤': '泽地萃',
    '离乾': '火天大有', '离兑': '火泽睽', '离离': '离为火', '离震': '火雷噬嗑',
    '离巽': '火风鼎', '离坎': '火水未济', '离艮': '火山旅', '离坤': '火地晋',
    '震乾': '雷天大壮', '震兑': '雷泽归妹', '震离': '雷火丰', '震震': '震为雷',
    '震巽': '雷风恒', '震坎': '雷水解', '震艮': '雷山小过', '震坤': '雷地豫',
    '巽乾': '风天小畜', '巽兑': '风泽中孚', '巽离': '风火家人', '巽震': '风雷益',
    '巽巽': '巽为风', '巽坎': '风水涣', '巽艮': '风山渐', '巽坤': '风地观',
    '坎乾': '水天需', '坎兑': '水泽节', '坎离': '水火既济', '坎震': '水雷屯',
    '坎巽': '水风井', '坎坎': '坎为水', '坎艮': '水山蹇', '坎坤': '水地比',
    '艮乾': '山天大畜', '艮兑': '山泽损', '艮离': '山火贲', '艮震': '山雷颐',
    '艮巽': '山风蛊', '艮坎': '山水蒙', '艮艮': '艮为山', '艮坤': '山地剥',
    '坤乾': '地天泰', '坤兑': '地泽临', '坤离': '地火明夷', '坤震': '地雷复',
    '坤巽': '地风升', '坤坎': '地水师', '坤艮': '地山谦', '坤坤': '坤为地',
}

# 六十四卦宫位
GUA_GONG_MAP = {
    '乾为天': '乾', '天风姤': '乾', '天山遁': '乾', '天地否': '乾',
    '风地观': '乾', '山地剥': '乾', '火地晋': '乾', '火天大有': '乾',
    '兑为泽': '兑', '泽水困': '兑', '泽地萃': '兑', '泽山咸': '兑',
    '水山蹇': '兑', '地山谦': '兑', '雷山小过': '兑', '雷泽归妹': '兑',
    '离为火': '离', '火山旅': '离', '火风鼎': '离', '火水未济': '离',
    '山水蒙': '离', '风水涣': '离', '天水讼': '离', '天火同人': '离',
    '震为雷': '震', '雷地豫': '震', '雷水解': '震', '雷风恒': '震',
    '地风升': '震', '水风井': '震', '泽风大过': '震', '泽雷随': '震',
    '巽为风': '巽', '风天小畜': '巽', '风火家人': '巽', '风雷益': '巽',
    '天雷无妄': '巽', '火雷噬嗑': '巽', '山雷颐': '巽', '山风蛊': '巽',
    '坎为水': '坎', '水泽节': '坎', '水雷屯': '坎', '水火既济': '坎',
    '泽火革': '坎', '雷火丰': '坎', '地火明夷': '坎', '地水师': '坎',
    '艮为山': '艮', '山火贲': '艮', '山天大畜': '艮', '山泽损': '艮',
    '火泽睽': '艮', '天泽履': '艮', '风泽中孚': '艮', '风山渐': '艮',
    '坤为地': '坤', '地雷复': '坤', '地泽临': '坤', '地天泰': '坤',
    '雷天大壮': '坤', '泽天夬': '坤', '水天需': '坤', '水地比': '坤',
}

# 六亲
LIU_QIN = ['父母', '兄弟', '子孙', '妻财', '官鬼']

# 六神
LIU_SHEN = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 地支五行
DI_ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
    '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 地支藏干
DI_ZHI_CANG_GAN = {
    '子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'],
    '卯': ['乙'], '辰': ['戊', '乙', '癸'], '巳': ['丙', '戊', '庚'],
    '午': ['丁', '己'], '未': ['己', '丁', '乙'], '申': ['庚', '壬', '戊'],
    '酉': ['辛'], '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲']
}

# 月令（按月支）
YUE_LING = {
    '寅': '春', '卯': '春', '辰': '春',
    '巳': '夏', '午': '夏', '未': '夏',
    '申': '秋', '酉': '秋', '戌': '秋',
    '亥': '冬', '子': '冬', '丑': '冬'
}

# 六神断语
LIU_SHEN_DUAN = {
    '青龙': {'吉': '喜庆临门，贵人相助', '凶': '乐极生悲，防过喜伤身'},
    '朱雀': {'吉': '文书有利，口舌生财', '凶': '口舌是非，防小人'},
    '勾陈': {'吉': '田土有利，稳定发展', '凶': '事多迟滞，防牵连'},
    '螣蛇': {'吉': '变化中求机', '凶': '虚惊怪异，防欺骗'},
    '白虎': {'吉': '武职有利，果断行事', '凶': '血光疾病，防意外'},
    '玄武': {'吉': '谋略得当，暗中得利', '凶': '防盗防骗，防暧昧'}
}

# 天干五行
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

# 五行生克
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}

# 世爻位置（按宫位和卦型）
# 八宫世爻律：本宫=6、一世=1、二世=2、三世=3、四世=4、五世=5、游魂=4、归魂=3。
# 每宫从本宫卦（八纯）起，依次按初爻→五爻变得到一世~五世，
# 再"四爻变回本宫"得游魂卦，最后"下卦归本宫"得归魂卦。
# 推导示例（兑宫，兑=☱=[1,1,0]，兑为泽=[1,1,0,1,1,0]，初→上）：
#   一世初变=[0,1,0,1,1,0]=坎下兑上=泽水困，世=1
#   五世=[0,0,1,0,0,0]=艮下坤上=地山谦，世=5
#   游魂=五世四爻变回=[0,0,1,1,0,0]=艮下震上=雷山小过，世=4
#   归魂=下卦归兑=[1,1,0,1,0,0]=兑下震上=雷泽归妹，世=3
SHI_YAO_MAP = {
    '乾': {'乾为天': 6, '天风姤': 1, '天山遁': 2, '天地否': 3,
           '风地观': 4, '山地剥': 5, '火地晋': 4, '火天大有': 3},
    '兑': {'兑为泽': 6, '泽水困': 1, '泽地萃': 2, '泽山咸': 3,
           '水山蹇': 4, '地山谦': 5, '雷山小过': 4, '雷泽归妹': 3},
    '离': {'离为火': 6, '火山旅': 1, '火风鼎': 2, '火水未济': 3,
           '山水蒙': 4, '风水涣': 5, '天水讼': 4, '天火同人': 3},
    '震': {'震为雷': 6, '雷地豫': 1, '雷水解': 2, '雷风恒': 3,
           '地风升': 4, '水风井': 5, '泽风大过': 4, '泽雷随': 3},
    '巽': {'巽为风': 6, '风天小畜': 1, '风火家人': 2, '风雷益': 3,
           '天雷无妄': 4, '火雷噬嗑': 5, '山雷颐': 4, '山风蛊': 3},
    '坎': {'坎为水': 6, '水泽节': 1, '水雷屯': 2, '水火既济': 3,
           '泽火革': 4, '雷火丰': 5, '地火明夷': 4, '地水师': 3},
    '艮': {'艮为山': 6, '山火贲': 1, '山天大畜': 2, '山泽损': 3,
           '火泽睽': 4, '天泽履': 5, '风泽中孚': 4, '风山渐': 3},
    '坤': {'坤为地': 6, '地雷复': 1, '地泽临': 2, '地天泰': 3,
           '雷天大壮': 4, '泽天夬': 5, '水天需': 4, '水地比': 3},
}

# 用神选取
YONG_SHEN_MAP = {
    '财运': '妻财', '事业': '官鬼', '工作': '官鬼', '婚姻': '妻财',
    '感情': '妻财', '健康': '子孙', '疾病': '官鬼', '考试': '父母',
    '学业': '父母', '失物': '妻财', '官司': '官鬼', '诉讼': '官鬼',
    '出行': '子孙', '旅行': '子孙', '求子': '子孙', '怀孕': '子孙',
    '搬家': '父母', '房屋': '父母', '交易': '妻财', '投资': '妻财',
}


class LiuYaoPan:
    """六爻排盘类"""
    
    @staticmethod
    def get_year_gan_zhi(year: int, month: int = 2, day: int = 5) -> Tuple[str, str]:
        """获取年干支（带立春切换）。

        历法约定：以"立春"为年柱分界，立春前仍属上一年。
        - 默认参数 (2, 5) 假定在立春后，直接返回 year 的年柱；
        - 传入实际公历月日时，若早于立春（约 2/4），返回 year-1 的年柱。

        若 lunar_python 可用，使用其精确立春时刻；否则按公历 2 月 4 日近似。
        退回近似时记录到 warnings（由调用方决定是否展示）。
        """
        effective_year = year
        if month == 1 or (month == 2 and day < 4):
            effective_year = year - 1
        # 精确化：用 lunar_python 检查立春
        try:
            from lunar_python import Solar
            solar = Solar.fromYmd(year, month, day)
            jie_qi = solar.getLunar().getJieQiTable()
            li_chun = jie_qi.get('立春')
            if li_chun is not None:
                # Solar 对象直接有 getYear/getMonth/.../getSecond
                cur_dt = datetime(
                    solar.getYear(), solar.getMonth(), solar.getDay(),
                    solar.getHour(), solar.getMinute(), solar.getSecond()
                )
                lc_dt = datetime(
                    li_chun.getYear(), li_chun.getMonth(), li_chun.getDay(),
                    li_chun.getHour(), li_chun.getMinute(), li_chun.getSecond()
                )
                effective_year = year if cur_dt >= lc_dt else year - 1
        except ImportError:
            # lunar_python 未安装，退回 2/4 近似（已在上方计算 effective_year）
            pass
        except Exception as exc:
            # lunar_python 内部异常：退回近似但记录，避免静默吞掉真实 bug
            import sys
            print(f"[警告] lunar_python 立春判断异常，退回 2/4 近似：{exc}", file=sys.stderr)

        gan_index = (effective_year - 4) % 10
        zhi_index = (effective_year - 4) % 12
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]

    # 节气近似日：每月的节气交接日（近似值，误差≤1天）
    # 格式：(节气月, 起始公历日近似) — 节气月以寅月(立春)为正月
    # 节气月份：寅1 卯2 辰3 巳4 午5 未6 申7 酉8 戌9 亥10 子11 丑12
    JIEQI_APPROX = [
        # (公历月, 节气交接近似日, 对应节气月名)
        (2, 4, '寅'),    # 立春 ≈ 2/4
        (3, 6, '卯'),    # 惊蛰 ≈ 3/6
        (4, 5, '辰'),    # 清明 ≈ 4/5
        (5, 6, '巳'),    # 立夏 ≈ 5/6
        (6, 6, '午'),    # 芒种 ≈ 6/6
        (7, 7, '未'),    # 小暑 ≈ 7/7
        (8, 8, '申'),    # 立秋 ≈ 8/8
        (9, 8, '酉'),    # 白露 ≈ 9/8
        (10, 8, '戌'),   # 寒露 ≈ 10/8
        (11, 7, '亥'),   # 立冬 ≈ 11/7
        (12, 7, '子'),   # 大雪 ≈ 12/7
        (1, 6, '丑'),    # 小寒 ≈ 1/6
    ]

    @staticmethod
    def get_solar_month_zhi(month: int, day: int, year: int = 2000) -> str:
        """根据公历月日推算节气月支（近似，回退用）。

        若 lunar_python 可用，优先使用精确节气（getPrevJieQi）。
        """
        # 首选：lunar_python 的精确"节"（立春/惊蛰/.../小寒）
        try:
            from lunar_python import Solar
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            # getPrevJieQi(False) 返回上一个"节"（非"气"）的 Solar
            prev_jie = lunar.getPrevJieQi(False)
            # 节气名（如"立春"）→ 月支
            jie_to_zhi = {
                '立春': '寅', '惊蛰': '卯', '清明': '辰', '立夏': '巳',
                '芒种': '午', '小暑': '未', '立秋': '申', '白露': '酉',
                '寒露': '戌', '立冬': '亥', '大雪': '子', '小寒': '丑',
            }
            prev_jie_name = prev_jie.getLunar().getJieQi() if hasattr(prev_jie, 'getLunar') else None
            # lunar_python 的 getPrevJieQi 返回的是 Lunar 或 Solar，需用 getName 或类似
            # 保险起见，尝试多种方式获取节气名
            if prev_jie_name is None:
                # 直接获取节气名（lunar_python JieQi 在 Lunar 上）
                try:
                    prev_jie_name = lunar.getPrevJieQiName()
                except Exception:
                    pass
            if prev_jie_name and prev_jie_name in jie_to_zhi:
                return jie_to_zhi[prev_jie_name]
        except Exception:
            pass

        # 回退：用近似表（误差≤1天）
        jq = LiuYaoPan.JIEQI_APPROX
        for i, (m, d, zhi) in enumerate(jq):
            if month == m:
                if day < d:
                    # 属于上一个节气月
                    prev = jq[(i - 1) % 12]
                    return prev[2]
                else:
                    return zhi
        # 兜底（不应到达）
        return '寅'

    @staticmethod
    def get_month_gan_zhi(year: int, month: int, day: int = 15) -> Tuple[str, str]:
        """获取月干支（按节气划分月支）

        五虎遁规则：甲己之年丙作首（寅月起丙寅），乙庚之岁戊为头，
                    丙辛之年庚寅起，丁壬壬寅顺水流，戊癸甲寅好追求。
        """
        # 月支：按节气确定
        zhi = LiuYaoPan.get_solar_month_zhi(month, day, year)
        zhi_index = DI_ZHI.index(zhi)

        # 月干：五虎遁 — 寅月的起始天干
        # 关键：年干必须基于立春判断后的"生效年份"
        year_gan, _ = LiuYaoPan.get_year_gan_zhi(year, month, day)
        # 寅月起始天干：甲→丙 乙→戊 丙→庚 丁→壬 戊→甲 己→丙 庚→戊 辛→庚 壬→壬 癸→甲
        yin_start = {'甲': 2, '乙': 4, '丙': 6, '丁': 8, '戊': 0,
                     '己': 2, '庚': 4, '辛': 6, '壬': 8, '癸': 0}
        start_gan_idx = yin_start.get(year_gan, 2)
        # 寅月=zhi_index=2，所以月份偏移 = zhi_index - 2
        month_offset = (zhi_index - 2) % 12
        gan_index = (start_gan_idx + month_offset) % 10
        gan = TIAN_GAN[gan_index]

        return gan, zhi
    
    @staticmethod
    def get_day_gan_zhi(date: datetime) -> Tuple[str, str]:
        """获取日干支（简化算法）
        
        基准日：1900年1月1日为甲戌日（干支序号=10，甲=0戌=10）
        经验证：1900-01-01 起算，diff=0 时 TIAN_GAN[0]=甲, DI_ZHI[10]=戌
        """
        # 基准日：1900 年 1 月 1 日为甲戌日
        base_date = datetime(1900, 1, 1)
        days_diff = (date - base_date).days
        
        gan_index = days_diff % 10
        # 甲戌日：干=0，支=10，所以支要加偏移 10
        zhi_index = (days_diff + 10) % 12
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    @staticmethod
    def get_hour_gan_zhi(day_gan: str, hour: int) -> Tuple[str, str]:
        """获取时干支
        
        五鼠遁规则：甲己起甲子，乙庚起丙子，丙辛起戊子，丁壬起庚子，戊癸起壬子
        """
        # 时支固定
        zhi_index = ((hour + 1) // 2) % 12
        zhi = DI_ZHI[zhi_index]
        
        # 时干根据日干推算（五鼠遁）
        gan_map = {'甲': 0, '乙': 2, '丙': 4, '丁': 6, '戊': 8,
                   '己': 0, '庚': 2, '辛': 4, '壬': 6, '癸': 8}
        start = gan_map.get(day_gan, 0)
        gan_index = (start + zhi_index) % 10
        gan = TIAN_GAN[gan_index]
        
        return gan, zhi
    
    @classmethod
    def time_to_gua(cls, date: datetime) -> Tuple[int, int, int]:
        """
        时间起卦（梅花易数法，用农历月日）
        返回：(上卦，下卦，动爻)
        
        公式：上卦=(年支+农历月+农历日) % 8，下卦=(年支+农历月+农历日+时支) % 8
        动爻=(年支+农历月+农历日+时支) % 6
        """
        year = date.year
        hour = date.hour
        
        # 年支数（1-12）— 立春切换后的生效年支
        _, year_zhi = cls.get_year_gan_zhi(year, date.month, date.day)
        year_zhi_num = DI_ZHI.index(year_zhi) + 1  # 子=1...亥=12
        
        # 时支数（1-12）
        hour_zhi_idx = cls._hour_to_zhi_index(hour)
        hour_zhi_num = hour_zhi_idx + 1  # 子时=1...亥时=12
        
        # 农历月日（近似转换）
        lunar_month, lunar_day = cls._solar_to_lunar_approx(date)
        
        total_upper = year_zhi_num + lunar_month + lunar_day
        total_lower = total_upper + hour_zhi_num
        
        shang_gua = total_upper % 8
        xia_gua = total_lower % 8
        dong_yao = total_lower % 6
        
        if shang_gua == 0:
            shang_gua = 8
        if xia_gua == 0:
            xia_gua = 8
        if dong_yao == 0:
            dong_yao = 6
        
        return shang_gua, xia_gua, dong_yao
    
    @staticmethod
    def _hour_to_zhi_index(hour: int) -> int:
        """小时转时支索引（0=子...11=亥）"""
        if hour == 23 or hour == 0:
            return 0  # 子时
        return (hour + 1) // 2
    
    @staticmethod
    def _solar_to_lunar_approx(date: datetime) -> Tuple[int, int]:
        """公历转农历（用于梅花易数时间起卦）。

        优先使用项目已依赖的 lunar_python（精确，支持任意年份）；
        若运行环境异常导致 lunar_python 不可用，再回退到 lunardate / sxtwl，
        最后才用粗略估算。返回 (农历月, 农历日)，闰月取绝对值（如闰六月按六月算）。
        """
        # 首选：lunar_python（已在 requirements.txt 中声明）
        try:
            from lunar_python import Solar
            lunar = Solar.fromYmd(date.year, date.month, date.day).getLunar()
            month = abs(lunar.getMonth())
            day = lunar.getDay()
            return month, day
        except Exception:
            pass

        # 次选：lunardate（若用户自行安装）
        try:
            import lunardate
            ld = lunardate.LunarDate.fromSolarDate(date.year, date.month, date.day)
            return abs(ld.month), ld.day
        except ImportError:
            pass

        # 再次选：sxtwl（寿星天文历）
        try:
            import sxtwl
            day_obj = sxtwl.fromSolar(date.year, date.month, date.day)
            return abs(day_obj.yue), day_obj.r
        except ImportError:
            pass

        # 最终回退：用内置近似表（2024-2030年春节对应的公历日期）
        # 数据来源：每年春节（正月初一）的公历日期
        new_year_dates = {
            2024: (2, 10),  # 2024年春节
            2025: (1, 29),  # 2025年春节
            2026: (2, 17),  # 2026年春节
            2027: (2, 6),   # 2027年春节
            2028: (1, 26),  # 2028年春节
            2029: (2, 13),  # 2029年春节
            2030: (2, 3),   # 2030年春节
        }

        year = date.year
        if year in new_year_dates:
            # 从该年春节起算天数差
            spring_m, spring_d = new_year_dates[year]
            spring = datetime(year, spring_m, spring_d)
            days_since_spring = (date - spring).days

            if days_since_spring < 0:
                # 在春节之前，属于上一农历年
                if year - 1 in new_year_dates:
                    prev_spring_m, prev_spring_d = new_year_dates[year - 1]
                    prev_spring = datetime(year - 1, prev_spring_m, prev_spring_d)
                    days_since_spring = (date - prev_spring).days
                else:
                    days_since_spring = 180  # 兜底

            if days_since_spring < 0:
                days_since_spring = 180

            # 近似每月30天
            lunar_month = days_since_spring // 30 + 1
            lunar_day = days_since_spring % 30 + 1
            lunar_month = min(lunar_month, 12)
            return lunar_month, lunar_day

        # 最终兜底：粗略估算（误差可能较大）
        # 公历月份约等于农历月份+1（2月≈正月，3月≈二月...）
        approx_month = date.month - 1
        if approx_month <= 0:
            approx_month = 12
        return approx_month, date.day
    
    @classmethod
    def number_to_gua(cls, numbers: List[int]) -> Tuple[int, int, int]:
        """数字起卦（梅花易数邵雍法）

        返回：(上卦，下卦，动爻)，取值范围上/下卦∈1-8、动爻∈1-6。
        - 三数及以上：上卦=数1%8，下卦=数2%8，动爻=数3%6（多余数字忽略）
        - 两数：上卦=数1%8，下卦=数2%8，动爻=(数1+数2)%6
        - 一数：上卦=数%8，下卦=(数//8)%8，动爻=数%6（邵雍大数起卦）
        余数为 0 时，上/下卦取 8、动爻取 6。
        """
        if len(numbers) >= 3:
            shang_gua = numbers[0] % 8
            xia_gua = numbers[1] % 8
            dong_yao = numbers[2] % 6
        elif len(numbers) == 2:
            shang_gua = numbers[0] % 8
            xia_gua = numbers[1] % 8
            dong_yao = (numbers[0] + numbers[1]) % 6
        else:
            n = numbers[0] if numbers else 0
            shang_gua = n % 8
            xia_gua = (n // 8) % 8
            dong_yao = n % 6

        if shang_gua == 0:
            shang_gua = 8
        if xia_gua == 0:
            xia_gua = 8
        if dong_yao == 0:
            dong_yao = 6

        return shang_gua, xia_gua, dong_yao
    
    @classmethod
    def coins_to_gua(cls, coins: List[int]) -> Tuple[List[int], List[int]]:
        """
        铜钱起卦（统一口径：每个数字代表该次投掷的"正面数/阳面数/字面数"）。

        传统铜钱：正面（阳/字/满文面）= 3，反面（阴/背/图案面）= 2。
        三枚组合：
          - 3 正 (3+3+3=9) = 老阳 → 本卦阳，变卦阴（动）
          - 2 正 1 反 (3+3+2=8) = 少阴 → 本卦阴，变卦阴（静）
          - 1 正 2 反 (3+2+2=7) = 少阳 → 本卦阳，变卦阳（静）
          - 0 正 (2+2+2=6) = 老阴 → 本卦阴，变卦阳（动）

        coins: 6 次投掷结果，每次为"正面数"（0/1/2/3），从初爻到上爻。
        返回：(本卦爻，变卦爻) 1=阳 0=阴
        """
        ben_gua = []
        bian_gua = []

        for coin in coins:
            if coin == 3:  # 老阳（动爻）
                ben_gua.append(1)
                bian_gua.append(0)
            elif coin == 0:  # 老阴（动爻）
                ben_gua.append(0)
                bian_gua.append(1)
            elif coin == 1:  # 少阳（静爻）
                ben_gua.append(1)
                bian_gua.append(1)
            elif coin == 2:  # 少阴（静爻）
                ben_gua.append(0)
                bian_gua.append(0)
            else:
                ben_gua.append(coin % 2)
                bian_gua.append(1 - coin % 2)

        return ben_gua, bian_gua
    
    @classmethod
    def get_gua_name(cls, shang_gua: int, xia_gua: int) -> str:
        """获取卦名"""
        shang = BA_GUA[shang_gua - 1]
        xia = BA_GUA[xia_gua - 1]
        key = shang + xia
        return LIU_SHI_SI_GUA.get(key, '未知卦')
    
    @classmethod
    def get_gua_gong(cls, gua_name: str) -> str:
        """获取卦宫"""
        return GUA_GONG_MAP.get(gua_name, '乾')
    
    @classmethod
    def get_shi_yao(cls, gua_name: str, gua_gong: str) -> int:
        """获取世爻位置（1-6）"""
        shi_map = SHI_YAO_MAP.get(gua_gong, {})
        return shi_map.get(gua_name, 1)
    
    @classmethod
    def get_yao_gan_zhi(cls, gua: str, yao_pos: int, is_wai_gua: bool) -> Tuple[str, str]:
        """
        获取某爻的干支
        yao_pos: 爻位（0-5，从初爻开始）
        is_wai_gua: 是否为外卦（上三爻）
        """
        # 地支从下往上排
        zhi_order = {
            '乾': ['子', '寅', '辰', '午', '申', '戌'],
            '兑': ['巳', '卯', '丑', '亥', '酉', '未'],
            '离': ['卯', '丑', '亥', '酉', '未', '巳'],
            '震': ['子', '寅', '辰', '午', '申', '戌'],
            '巽': ['丑', '亥', '酉', '未', '巳', '卯'],
            '坎': ['寅', '辰', '午', '申', '戌', '子'],
            '艮': ['辰', '午', '申', '戌', '子', '寅'],
            '坤': ['未', '巳', '卯', '丑', '亥', '酉'],
        }
        
        zhi = zhi_order.get(gua, ['子', '寅', '辰', '午', '申', '戌'])[yao_pos]
        
        # 天干根据纳甲
        gan_list = NA_JIA_GAN.get(gua, ['甲', '甲', '甲', '甲', '甲', '甲'])
        gan = gan_list[yao_pos]
        
        return gan, zhi
    
    @classmethod
    def get_liu_qin(cls, gua_gong_wuxing: str, yao_wuxing: str) -> str:
        """
        根据卦宫五行和爻五行确定六亲
        """
        if yao_wuxing == gua_gong_wuxing:
            return '兄弟'
        elif WUXING_SHENG.get(yao_wuxing) == gua_gong_wuxing:
            return '父母'
        elif WUXING_SHENG.get(gua_gong_wuxing) == yao_wuxing:
            return '子孙'
        elif WUXING_KE.get(yao_wuxing) == gua_gong_wuxing:
            return '官鬼'
        elif WUXING_KE.get(gua_gong_wuxing) == yao_wuxing:
            return '妻财'
        else:
            return '兄弟'
    
    @classmethod
    def get_liu_shen(cls, day_gan: str, yao_pos: int) -> str:
        """
        根据日干和爻位确定六神
        
        标准规则：甲乙日起青龙，丙丁日起朱雀，戊日起勾陈，
        己日起螣蛇，庚辛日起白虎，壬癸日起玄武。
        初爻起对应六神，依次往上排。
        """
        gan_map = {'甲': 0, '乙': 0, '丙': 1, '丁': 1, '戊': 2,
                   '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5}
        start = gan_map.get(day_gan, 0)
        shen_index = (start + yao_pos) % 6
        return LIU_SHEN[shen_index]

    # 六冲：相冲的地支对
    DI_ZHI_CHONG = {
        '子': '午', '午': '子', '丑': '未', '未': '丑',
        '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳',
    }

    @staticmethod
    def get_xun_kong(day_gan: str, day_zhi: str) -> Tuple[str, str]:
        """计算日柱所在旬的"旬空"（空亡地支）。

        六十甲子分六旬，每旬 10 个干支，但地支 12 个，故每旬有两个地支轮不上，即为空亡。
        - 甲子旬（甲子~癸酉）：空戌亥
        - 甲戌旬（甲戌~癸未）：空申酉
        - 甲申旬（甲申~癸巳）：空午未
        - 甲午旬（甲午~癸卯）：空辰巳
        - 甲辰旬（甲辰~癸丑）：空寅卯
        - 甲寅旬（甲寅~癸亥）：空子丑
        """
        gan_idx = TIAN_GAN.index(day_gan)
        zhi_idx = DI_ZHI.index(day_zhi)
        # 求六十甲子序号（0-59）
        n = (6 * gan_idx - 5 * zhi_idx) % 60
        # 每旬首为 甲子(0)、甲戌(10)、甲申(20)、甲午(30)、甲辰(40)、甲寅(50)
        xun_idx = n // 10  # 0~5
        kong_pairs = [('戌', '亥'), ('申', '酉'), ('午', '未'),
                      ('辰', '巳'), ('寅', '卯'), ('子', '丑')]
        return kong_pairs[xun_idx]

    @classmethod
    def get_yue_po(cls, month_zhi: str) -> str:
        """月破：与月支相冲的地支。"""
        return cls.DI_ZHI_CHONG.get(month_zhi, '')

    @classmethod
    def find_fu_fei_shen(
        cls,
        yong_shen: str,
        yao_list: List[Dict],
        gua_gong: str,
        gua_gong_wuxing: str,
    ) -> Optional[Dict]:
        """查找伏神与飞神。

        当用神六亲在本卦六爻中不出现时，从本宫首卦（八纯卦）借用：
        - 伏神：本宫首卦中该六亲所在爻的干支（伏于本卦某爻之下）
        - 飞神：本卦中相同爻位的爻

        返回 None 表示用神已上卦，无需伏神；否则返回
        {'伏神干支': '...', '伏神五行': '...', '飞神爻位': int, '飞神干支': '...', '飞神六亲': '...'}
        """
        # 用神是否上卦
        if any(y['六亲'] == yong_shen for y in yao_list):
            return None

        # 遍历本宫首卦（八纯卦）的 6 爻，找用神六亲所在爻位
        # 八纯卦上下卦同，六亲分布按爻位固定；直接用卦宫字符调用 get_yao_gan_zhi
        target_yao_pos = None
        target_gan_zhi = None
        for yao_pos in range(6):
            is_wai = yao_pos >= 3
            gan, zhi = cls.get_yao_gan_zhi(gua_gong, yao_pos, is_wai)
            wuxing = DI_ZHI_WUXING[zhi]
            liu_qin = cls.get_liu_qin(gua_gong_wuxing, wuxing)
            if liu_qin == yong_shen:
                target_yao_pos = yao_pos
                target_gan_zhi = (gan, zhi)
                target_wuxing = wuxing
                break

        if target_yao_pos is None:
            return None

        # 找本卦中相同爻位的飞神
        fei_yao = next((y for y in yao_list if y['爻位'] == target_yao_pos + 1), None)
        if fei_yao is None:
            return None

        return {
            '伏神爻位': target_yao_pos + 1,
            '伏神干支': f"{target_gan_zhi[0]}{target_gan_zhi[1]}",
            '伏神五行': target_wuxing,
            '飞神爻位': fei_yao['爻位'],
            '飞神干支': fei_yao['干支'],
            '飞神六亲': fei_yao['六亲'],
        }

    @classmethod
    def get_bian_gua(cls, shang_gua: int, xia_gua: int, dong_yao: 'int|List[int]') -> str:
        """获取变卦：动爻变阴阳后得到的新卦。

        dong_yao 可传入单个动爻编号（1-6，向后兼容）或动爻列表（支持多动爻）。
        """
        if isinstance(dong_yao, int):
            dong_list = [dong_yao] if dong_yao else []
        else:
            dong_list = [d for d in dong_yao if 1 <= d <= 6]
        if not dong_list:
            return '无'

        # 动爻范围 1-6：1-3为下卦，4-6为上卦
        # 先确定本卦上下卦的阴阳爻
        shang = BA_GUA[shang_gua - 1]
        xia = BA_GUA[xia_gua - 1]

        # 八卦的二进制表示（从初爻到上爻），见模块级 GUA_BINARY
        xia_yao = list(GUA_BINARY.get(xia, (0, 0, 0)))
        shang_yao = list(GUA_BINARY.get(shang, (0, 0, 0)))
        yao_6 = xia_yao + shang_yao  # [初,二,三,四,五,上]

        # 所有动爻变（1→0，0→1）
        for dong in dong_list:
            yao_6[dong - 1] = 1 - yao_6[dong - 1]

        # 拆回上下卦
        new_xia_yao = yao_6[:3]
        new_shang_yao = yao_6[3:]

        # 反查八卦（用模块级 GUA_BINARY 反查）
        new_xia = next((g for g, v in GUA_BINARY.items() if v == tuple(new_xia_yao)), '乾')
        new_shang = next((g for g, v in GUA_BINARY.items() if v == tuple(new_shang_yao)), '乾')

        # 查卦名
        key = new_shang + new_xia
        return LIU_SHI_SI_GUA.get(key, '未知卦')
    
    @classmethod
    def get_wang_shuai(cls, yao_wuxing: str, month_zhi: str, day_zhi: str) -> str:
        """
        判断爻的旺衰（基于月令）
        
        标准规则：当令者旺，令生者相，生令者休，克令者囚，令克者死
        例：午月(火)→火旺、木(生火)相、水(克火)囚、金(火克)死、土(火生土)休
        """
        month_wuxing = DI_ZHI_WUXING.get(month_zhi, '土')
        
        if yao_wuxing == month_wuxing:
            return '旺'       # 当令
        elif WUXING_SHENG.get(month_wuxing) == yao_wuxing:
            return '相'       # 令生我
        elif WUXING_SHENG.get(yao_wuxing) == month_wuxing:
            return '休'       # 我生令
        elif WUXING_KE.get(yao_wuxing) == month_wuxing:
            return '囚'       # 我克令
        elif WUXING_KE.get(month_wuxing) == yao_wuxing:
            return '死'       # 令克我
        else:
            return '平'
    
    @classmethod
    def get_shi_ying_relation(cls, shi_wuxing: str, ying_wuxing: str) -> Dict:
        """
        分析世应关系
        """
        if shi_wuxing == ying_wuxing:
            return {'关系': '比和', '吉凶': '平', '说明': '势均力敌，需努力争取'}
        elif WUXING_SHENG.get(shi_wuxing) == ying_wuxing:
            return {'关系': '世生应', '吉凶': '凶', '说明': '我生对方，付出多回报少'}
        elif WUXING_SHENG.get(ying_wuxing) == shi_wuxing:
            return {'关系': '应生世', '吉凶': '吉', '说明': '对方生我，贵人相助'}
        elif WUXING_KE.get(shi_wuxing) == ying_wuxing:
            return {'关系': '世克应', '吉凶': '平', '说明': '我克对方，主动可控'}
        elif WUXING_KE.get(ying_wuxing) == shi_wuxing:
            return {'关系': '应克世', '吉凶': '凶', '说明': '对方克我，压力大阻力大'}
        return {'关系': '未知', '吉凶': '平', '说明': '关系不明'}
    
    @classmethod
    def get_liu_shen_duan(cls, liu_shen: str, ji_xiong: str) -> str:
        """获取六神断语"""
        return LIU_SHEN_DUAN.get(liu_shen, {}).get(ji_xiong, '待分析')
    
    @classmethod
    def analyze_duan_gua(cls, result: Dict) -> Dict:
        """
        完整断卦分析
        """
        yao_list = result.get('六爻', [])
        yong_shen = result.get('用神', '妻财')
        month_zhi = result.get('月支', '子')
        day_zhi = result.get('日支', '子')
        shi_yao = result.get('世爻', 1)
        ying_yao = result.get('应爻', 4)
        
        # 找用神爻
        yong_shen_yao = None
        for yao in yao_list:
            if yao['六亲'] == yong_shen:
                yong_shen_yao = yao
                break
        
        # 用神旺衰
        yong_shen_wang_shuai = '平'
        if yong_shen_yao:
            yong_shen_wang_shuai = cls.get_wang_shuai(
                yong_shen_yao['五行'], month_zhi, day_zhi
            )
        
        # 世应关系
        shi_yao_info = None
        ying_yao_info = None
        for yao in yao_list:
            if yao['爻位'] == shi_yao:
                shi_yao_info = yao
            if yao['爻位'] == ying_yao:
                ying_yao_info = yao
        
        shi_ying_relation = {'关系': '未知', '吉凶': '平', '说明': '待分析'}
        if shi_yao_info and ying_yao_info:
            shi_ying_relation = cls.get_shi_ying_relation(
                shi_yao_info['五行'], ying_yao_info['五行']
            )
        
        # 动爻分析
        dong_yao_list = [y for y in yao_list if y.get('动爻', False)]
        dong_yao_duan = []
        for dy in dong_yao_list:
            if dy['六亲'] == yong_shen:
                dong_yao_duan.append(f"用神动，变化中求机会")
            elif dy['六亲'] == '兄弟':
                dong_yao_duan.append(f"兄弟动，防破财竞争")
            elif dy['六亲'] == '官鬼':
                dong_yao_duan.append(f"官鬼动，防压力是非")
            elif dy['六亲'] == '父母':
                dong_yao_duan.append(f"父母动，文书有利")
            elif dy['六亲'] == '子孙':
                dong_yao_duan.append(f"子孙动，财源广进")
            elif dy['六亲'] == '妻财':
                dong_yao_duan.append(f"妻财动，财运变化")
        
        # 六神断语
        liu_shen_duan = []
        if yong_shen_yao:
            ji_xiong = '吉' if yong_shen_wang_shuai in ['旺', '相'] else '凶'
            liu_shen_duan.append(
                f"{yong_shen_yao['六神']}临用神：{cls.get_liu_shen_duan(yong_shen_yao['六神'], ji_xiong)}"
            )
        
        # 吉凶评分（0-100）
        score = 50
        if yong_shen_wang_shuai == '旺':
            score += 20
        elif yong_shen_wang_shuai == '相':
            score += 10
        elif yong_shen_wang_shuai == '死':
            score -= 20
        elif yong_shen_wang_shuai == '囚':
            score -= 10
        
        if shi_ying_relation['吉凶'] == '吉':
            score += 15
        elif shi_ying_relation['吉凶'] == '凶':
            score -= 15
        
        if dong_yao_list:
            # 有动爻，看吉凶
            for dy in dong_yao_list:
                if dy['六亲'] in ['子孙', '妻财']:
                    score += 5
                elif dy['六亲'] in ['兄弟', '官鬼']:
                    score -= 5
        
        score = max(0, min(100, score))
        
        # 吉凶判断
        if score >= 70:
            ji_xiong_pan_duan = '大吉'
            jian_yi = '卦象大吉，宜积极行动，把握良机'
        elif score >= 55:
            ji_xiong_pan_duan = '吉'
            jian_yi = '卦象偏吉，可顺势而为，注意细节'
        elif score >= 45:
            ji_xiong_pan_duan = '平'
            jian_yi = '卦象平稳，宜守不宜攻，等待时机'
        elif score >= 30:
            ji_xiong_pan_duan = '凶'
            jian_yi = '卦象偏凶，宜谨慎行事，防小人'
        else:
            ji_xiong_pan_duan = '大凶'
            jian_yi = '卦象大凶，宜韬光养晦，暂避锋芒'
        
        # 趋避建议
        qu_bi = []
        if yong_shen_wang_shuai in ['死', '囚']:
            qu_bi.append('用神衰弱，宜补旺用神五行')
        if shi_ying_relation['关系'] == '应克世':
            qu_bi.append('应克世，防对方施压，宜退让')
        if shi_ying_relation['关系'] == '世生应':
            qu_bi.append('世生应，付出多，宜控制投入')
        for dy in dong_yao_list:
            if dy['六亲'] == '兄弟':
                qu_bi.append('兄弟动，防破财，不宜投资')
            elif dy['六亲'] == '官鬼':
                qu_bi.append('官鬼动，防是非，谨言慎行')
        
        if not qu_bi:
            qu_bi.append('卦象无大碍，顺势而为即可')
        
        return {
            '用神旺衰': yong_shen_wang_shuai,
            '世应关系': shi_ying_relation,
            '动爻分析': dong_yao_duan,
            '六神断语': liu_shen_duan,
            '吉凶评分': score,
            '吉凶判断': ji_xiong_pan_duan,
            '建议': jian_yi,
            '趋避': qu_bi
        }


def liuyao_pan(
    date_str: Optional[str] = None,
    numbers: Optional[str] = None,
    coins: Optional[str] = None,
    question: str = '通用'
) -> Dict:
    """
    六爻排盘主函数
    """
    # 时间处理
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    else:
        dt = datetime.now()

    # 晚子时（23:00-23:59）日柱归次日（与 ziwei_chart.py 的"子时归次日"约定一致）
    # 时柱仍用 "子" 时，但日干用次日的日干来遁时干
    if dt.hour >= 23:
        day_dt_for_pillar = dt + timedelta(days=1)
    else:
        day_dt_for_pillar = dt

    # 干支
    # - 年柱、月柱：基于实际年月日（带立春/节气切换）
    # - 日柱：基于 day_dt_for_pillar（晚子时归次日）
    # - 时柱：基于 day_dt_for_pillar 的日干遁时干
    year_gan, year_zhi = LiuYaoPan.get_year_gan_zhi(dt.year, dt.month, dt.day)
    month_gan, month_zhi = LiuYaoPan.get_month_gan_zhi(dt.year, dt.month, dt.day)
    day_gan, day_zhi = LiuYaoPan.get_day_gan_zhi(day_dt_for_pillar)
    hour_gan, hour_zhi = LiuYaoPan.get_hour_gan_zhi(day_gan, dt.hour)
    
    # 起卦
    # ben_gua_yao / bian_gua_yao 仅铜钱路径有值（其余路径为 None）；
    # dong_yao_list 统一为动爻列表（保留多动爻），dong_yao 取首个用于向后兼容。
    ben_gua_yao: Optional[List[int]] = None
    bian_gua_yao: Optional[List[int]] = None
    dong_yao_list: List[int] = []

    if coins:
        try:
            coin_list = [int(x.strip()) for x in coins.split(',')]
        except ValueError as exc:
            raise ValueError(
                f"铜钱起卦的每个数字必须为整数（正面数 0-3），解析失败：{exc}"
            ) from exc
        if len(coin_list) != 6:
            raise ValueError(
                f"铜钱起卦需要 6 个数字（6 次投掷的正面数/阳面数 0-3），当前 {len(coin_list)} 个"
            )
        invalid = [c for c in coin_list if not (0 <= c <= 3)]
        if invalid:
            raise ValueError(
                f"铜钱起卦的每个数字必须为 0-3（正面数），存在非法值：{invalid}"
            )
        ben_gua_yao, bian_gua_yao = LiuYaoPan.coins_to_gua(coin_list)
        # 从本卦六爻直接二进制重建上下卦（不用 sum%8 反推，那是错的）
        # 二进制→先天卦序编号，见模块级 BINARY_TO_GUA_IDX
        xia_gua = BINARY_TO_GUA_IDX[tuple(ben_gua_yao[:3])]
        shang_gua = BINARY_TO_GUA_IDX[tuple(ben_gua_yao[3:])]
        # 动爻 = 本卦与变卦阴阳不同的爻（保留全部，不丢弃）
        dong_yao_list = [
            i + 1 for i, (b, v) in enumerate(zip(ben_gua_yao, bian_gua_yao)) if b != v
        ]
        qi_gua_fang_shi = '铜钱'
    elif numbers:
        num_list = [int(x.strip()) for x in numbers.split(',')]
        shang_gua, xia_gua, dong_yao_single = LiuYaoPan.number_to_gua(num_list)
        dong_yao_list = [dong_yao_single] if dong_yao_single else []
        qi_gua_fang_shi = '数字'
    else:
        shang_gua, xia_gua, dong_yao_single = LiuYaoPan.time_to_gua(dt)
        dong_yao_list = [dong_yao_single] if dong_yao_single else []
        qi_gua_fang_shi = '时间'

    dong_yao = dong_yao_list[0] if dong_yao_list else 0  # 向后兼容字段
    
    # 卦名卦宫
    gua_name = LiuYaoPan.get_gua_name(shang_gua, xia_gua)
    gua_gong = LiuYaoPan.get_gua_gong(gua_name)
    gua_gong_wuxing = BA_GUA_WUXING[gua_gong]
    shi_yao = LiuYaoPan.get_shi_yao(gua_name, gua_gong)
    ying_yao = ((shi_yao - 1 + 3) % 6) + 1
    
    # 下卦和上卦名
    xia_gua_name = BA_GUA[xia_gua - 1]
    shang_gua_name = BA_GUA[shang_gua - 1]

    # 预计算六爻阴阳（铜钱路径直接用实际本卦爻；其余路径从卦编号重建二进制）
    # 八卦二进制（初爻→上爻）：乾111 兑110 离101 震100 巽011 坎010 艮001 坤000
    if ben_gua_yao is not None:
        yao_yin_yang_bits = list(ben_gua_yao)
    else:
        yao_yin_yang_bits = list(GUA_BINARY[xia_gua_name]) + list(GUA_BINARY[shang_gua_name])

    # 六爻排布
    yao_list = []
    for i in range(6):
        yao_pos = i  # 0-5
        is_wai_gua = i >= 3
        gua_for_yao = xia_gua_name if i < 3 else shang_gua_name

        gan, zhi = LiuYaoPan.get_yao_gan_zhi(gua_for_yao, yao_pos, is_wai_gua)
        yao_wuxing = DI_ZHI_WUXING[zhi]
        liu_qin = LiuYaoPan.get_liu_qin(gua_gong_wuxing, yao_wuxing)
        liu_shen = LiuYaoPan.get_liu_shen(day_gan, yao_pos)

        # 判断阴阳（用预计算的本卦爻位阴阳，而非无关公式）
        yao_yang = yao_yin_yang_bits[i]
        # 判断是否动爻（支持多动爻）
        is_dong = (i + 1) in dong_yao_list

        yao_list.append({
            '爻位': i + 1,
            '爻名': ['初', '二', '三', '四', '五', '上'][i],
            '阴阳': '阳' if yao_yang else '阴',
            '干支': f'{gan}{zhi}',
            '五行': yao_wuxing,
            '六亲': liu_qin,
            '六神': liu_shen,
            '世应': '世' if i + 1 == shi_yao else ('应' if i + 1 == ying_yao else ''),
            '动爻': is_dong,
        })
    
    # 用神
    yong_shen = YONG_SHEN_MAP.get(question, '妻财')

    # 旬空（基于日柱）+ 月破（与月支相冲的日支）
    xun_kong = LiuYaoPan.get_xun_kong(day_gan, day_zhi)
    yue_po = LiuYaoPan.get_yue_po(month_zhi)

    # 伏神/飞神（用神不上卦时启用）
    fu_fei_shen = LiuYaoPan.find_fu_fei_shen(
        yong_shen=yong_shen,
        yao_list=yao_list,
        gua_gong=gua_gong,
        gua_gong_wuxing=gua_gong_wuxing,
    )

    # 变卦（传完整动爻列表，支持多动爻）
    bian_gua = LiuYaoPan.get_bian_gua(shang_gua, xia_gua, dong_yao_list)
    
    # 断卦分析
    yong_shen_yao = [y for y in yao_list if y['六亲'] == yong_shen]
    yong_shen_wang = len(yong_shen_yao) > 0
    
    # 断卦分析 v3.0.0
    temp_result = {
        '六爻': yao_list,
        '用神': yong_shen,
        '月支': month_zhi,
        '日支': day_zhi,
        '世爻': shi_yao,
        '应爻': ying_yao,
    }
    duan_gua = LiuYaoPan.analyze_duan_gua(temp_result)
    
    result = {
        '起卦方式': qi_gua_fang_shi,
        '公历时间': dt.strftime('%Y 年 %m 月 %d 日 %H 时 %M 分'),
        '农历时间': f'{year_gan}{year_zhi}年 {month_gan}{month_zhi}月 {day_gan}{day_zhi}日 {hour_gan}{hour_zhi}时',
        '四柱': f'{year_gan}{year_zhi}  {month_gan}{month_zhi}  {day_gan}{day_zhi}  {hour_gan}{hour_zhi}',
        '本卦': gua_name,
        '卦宫': gua_gong,
        '卦宫五行': gua_gong_wuxing,
        '上下卦': f'{shang_gua_name}上{xia_gua_name}下',
        '世爻': shi_yao,
        '应爻': ying_yao,
        '动爻': dong_yao,
        '动爻列表': dong_yao_list,
        '变卦': bian_gua,
        '六爻': yao_list,
        '问事类型': question,
        '用神': yong_shen,
        '用神爻': yong_shen_yao[0] if yong_shen_yao else None,
        '月支': month_zhi,
        '日支': day_zhi,
        '旬空': xun_kong,
        '月破': yue_po,
        '伏神飞神': fu_fei_shen,
        '断卦分析': duan_gua,
    }
    
    return result


def format_output(result: Dict) -> str:
    """格式化输出"""
    output = []
    
    output.append("【卦象结果】")
    output.append(f"• 起卦方式：{result['起卦方式']}")
    output.append(f"• 公历时间：{result['公历时间']}")
    output.append(f"• 农历时间：{result['农历时间']}")
    output.append(f"• 四柱：{result['四柱']}")
    output.append("")
    output.append("【本卦】")
    output.append(f"• 卦名：{result['本卦']}（{result['卦宫']}宫）")
    output.append(f"• 卦宫五行：{result['卦宫五行']}")
    output.append(f"• 世爻：第{result['世爻']}爻")
    output.append(f"• 应爻：第{result['应爻']}爻")
    dong_list = result.get('动爻列表') or ([result['动爻']] if result.get('动爻') else [])
    if dong_list:
        dong_str = '、'.join(f"第{d}爻" for d in dong_list)
        output.append(f"• 动爻：{dong_str}")
        output.append(f"• 变卦：{result['变卦']}")
    output.append("")
    output.append("【六爻排布】")
    output.append("爻位  阴阳  干支  六亲  六神  世应")
    output.append("─" * 45)
    for yao in reversed(result['六爻']):
        yin_yang = '━━━' if yao['阴阳'] == '阳' else '━ ━'
        shi_ying = f" {yao['世应']}" if yao['世应'] else '    '
        dong = '○' if yao['动爻'] else ' '
        output.append(f"{yao['爻名']}爻  {yin_yang}{dong} {yao['干支']} {yao['六亲']} {yao['六神']}{shi_ying}")
    output.append("")
    output.append("【用神分析】")
    output.append(f"• 问事类型：{result['问事类型']}")
    output.append(f"• 用神：{result['用神']}")
    if result['用神爻']:
        yong = result['用神爻']
        output.append(f"• 用神落爻：第{yong['爻位']}爻（{yong['干支']}）")
        output.append(f"• 用神五行：{yong['五行']}")
        output.append(f"• 临六神：{yong['六神']}")
    else:
        output.append("• 用神不上卦")
    # 旬空与月破（历法辅助信息）
    xk = result.get('旬空')
    if xk:
        output.append(f"• 旬空：{xk[0]}、{xk[1]}")
    yp = result.get('月破')
    if yp:
        output.append(f"• 月破：{yp}（日支若临月破则主虚耗）")
    # 伏神/飞神（用神不上卦时显示）
    ff = result.get('伏神飞神')
    if ff:
        output.append(
            f"• 伏神：第{ff['伏神爻位']}爻 {ff['伏神干支']}（{ff['伏神五行']}）"
            f" — 飞于本卦 {ff['飞神干支']}（{ff['飞神六亲']}）之下"
        )
    output.append("")
    output.append("【断卦分析】")
    duan_gua = result.get('断卦分析', {})
    output.append(f"• 用神旺衰：{duan_gua.get('用神旺衰', '待分析')}")
    shi_ying = duan_gua.get('世应关系', {})
    output.append(f"• 世应关系：{shi_ying.get('关系', '待分析')}（{shi_ying.get('吉凶', '')}）— {shi_ying.get('说明', '')}")
    if duan_gua.get('动爻分析'):
        for dy in duan_gua['动爻分析']:
            output.append(f"• 动爻：{dy}")
    if duan_gua.get('六神断语'):
        for ls in duan_gua['六神断语']:
            output.append(f"• {ls}")
    output.append(f"• 吉凶评分：{duan_gua.get('吉凶评分', 50)}/100")
    output.append(f"• 吉凶判断：{duan_gua.get('吉凶判断', '待分析')}")
    output.append(f"• 建议：{duan_gua.get('建议', '待分析')}")
    if duan_gua.get('趋避'):
        output.append("")
        output.append("【趋吉避凶】")
        for tb in duan_gua['趋避']:
            output.append(f"• {tb}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='六爻纳甲排盘工具 v3.0.0')
    parser.add_argument('--date', '-d', type=str, help='日期时间 (YYYY-MM-DD HH:MM)')
    parser.add_argument('--numbers', '-n', type=str, help='数字起卦 (逗号分隔)')
    parser.add_argument('--coins', '-c', type=str, help='铜钱起卦 (6 次正面数/字面数 0-3，逗号分隔)')
    parser.add_argument('--question', '-q', type=str, default='通用', help='问事类型')
    parser.add_argument('--json', '-j', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    try:
        result = liuyao_pan(args.date, args.numbers, args.coins, args.question)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_output(result))
            
    except Exception as e:
        print(f"排盘错误：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
