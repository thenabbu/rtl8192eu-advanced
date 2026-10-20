# Linux driver control-surface map — harvested evidence

Source-grounded map of `driver/` (Realtek 5.11.2.1 base) collected by the
`deleg_c96e46f4` fan-out run (task 1, 2026-10-20). The run was interrupted
before final synthesis; this file preserves its collected evidence verbatim
(query → output), so the synthesis can be done without re-running the greps.
Transcript: `/opt/data/cache/delegation/live/deleg_c96e46f4/task-0.log`.

Note: long outputs are head/tail-truncated exactly as the run's transcript
preserved them; the truncation marker `…(+N chars)` is kept where present.

## Collected evidence

### 12:41:50  terminal

**Query:**

```
python3 - <<'PY' from pathlib import ...
```

**Output:**

```
exists= True
files= 593
suffixes= {'.c': 190, '.conf': 1, '.h': 389, '.md': 1, '.mk': 3, '.sh': 2, '.ur-safe': 1, '[none]': 6}
DIR . direct_files=10
DIR core direct_files=45
DIR hal direct_files=16
DIR include direct_files=260
DIR os_dep direct_files=2
DIR platform direct_files=17
DIR core/crypto direct_files=21
DIR core/efuse direct_files=1
DIR core/mesh direct_files=6
DIR 
```

### 12:41:51  search_files

**Query:**

```
\b(monitor|MONITOR|radiotap|injection...
```

**Output:**

```
{"total_count": 200, "matches_format": "path-grouped: each file path on its own line, followed by indented '<line>: <content>' rows for matches in that file", "matches_text": "/opt/data/repos/rtl8192eu-advanced/driver/include/osdep_intf.h\n 100: #include \"../os_dep/linux/rtw_proc.h\"\n/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/os_intfs.c\n 31: module_param(rtw_la_mode_en, int, 0644);\ …(+13696 chars)
```

### 12:42:25  terminal

**Query:**

```
rg --files /opt/data/repos/rtl8192eu-...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/core/crypto/aes-ccm.c
/opt/data/repos/rtl8192eu-advanced/driver/core/crypto/aes-ctr.c
/opt/data/repos/rtl8192eu-advanced/driver/core/crypto/aes-gcm.c
/opt/data/repos/rtl8192eu-advanced/driver/core/crypto/aes-internal-enc.c
/opt/data/repos/rtl8192eu-advanced/driver/core/crypto/aes-internal.c
/opt/data/repos/rtl8192eu-advanced/driver/core/cr 
```

### 12:42:26  terminal

**Query:**

```
rg -n --glob '*.[ch]' '^([a-zA-Z_][a-...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_recv.c:4318:s32 rtw_recv_entry(union recv_frame *precvframe)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/rtl8192eu_xmit.c:429:s32 rtl8192eu_xmitframe_complete(_adapter *padapter, struct xmit_priv *pxmitpriv, struct xmit_buf *pxmitbuf)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/rtl8192eu_xmit.c:734:s32 r 
```

### 12:42:26  terminal

**Query:**

```
rg -n --glob '*.[ch]' '(FirmwareDownl...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c:382:extern char *rtw_fw_file_path;
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c:388:FirmwareDownload8192E(
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c:421:		fwfilepath = rtw_fw_file_path;
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8 
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 2 '(usb_device_id|USB_DEVICE...
```

**Output:**

```
{"output": "36-\n37-extern int pm_netdev_open(struct net_device *pnetdev, u8 bnormal);\n38:static int rtw_suspend(struct usb_interface *intf, pm_message_t message);\n39:static int rtw_resume(struct usb_interface *intf);\n40-\n41-\n42:static int rtw_drv_init(struct usb_interface *pusb_intf, const struct usb_device_id *pdid);\n43-static void rtw_dev_remove(struct usb_interface *pusb_intf);\n44-\n--\ …(+7252 chars)
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 2 '^(static )?(u8|int|void|s...
```

**Output:**

```
36-
37-extern int pm_netdev_open(struct net_device *pnetdev, u8 bnormal);
38:static int rtw_suspend(struct usb_interface *intf, pm_message_t message);
39:static int rtw_resume(struct usb_interface *intf);
40-
41-
--
629-}
630-
631:static void usb_dvobj_deinit(struct usb_interface *usb_intf)
632-{
633-	struct dvobj_priv *dvobj = usb_get_intfdata(usb_intf);
--
758-}
759-
 
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 2 '^(u8|void) rtw_(init_drv_...
```

**Output:**

```
2785-
2786-
2787:u8 rtw_init_drv_sw(_adapter *padapter)
2788-{
2789-	u8	ret8 = _SUCCESS;
--
3067-}
3068-
3069:u8 rtw_free_drv_sw(_adapter *padapter)
3070-{
3071-
--
3216-
3217-#ifdef CONFIG_IOCTL_CFG80211
3218:	rtw_cfg80211_init_wdev_data(padapter);
3219-#endif
3220-
--
3874-
3875-		#ifdef CONFIG_IOCTL_CFG80211
3876:		rtw_cfg80211_init_wdev_data(padapter);
3 
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 2 '^(s32|u32|int|void|BOOLEA...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c-341-}
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c-342-
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_init.c:343:static s32 _FWFreeToGo8192E(_adapter *adapter, u32 min_cnt, u32 timeout_ms)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_hal_i 
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 2 '^(static )?(u32|s32|void|...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-91-}
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-92-
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c:93:static void rtl8192eu_interface_configure(_adapter *padapter)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-94-{
/opt/data/rep 
```

### 12:43:09  terminal

**Query:**

```
rg -n -C 1 '^(int|s32|u8|void|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_recv.c-2859-
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_recv.c:2860:static int rtw_recv_indicatepkt_check(union recv_frame *rframe, u8 *ehdr_pos, u32 pkt_len)
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_recv.c-2861-{
--
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_recv.c-4317-
/opt/data/repos/rtl8192eu-advance 
```

### 12:43:37  terminal

**Query:**

```
rg -n -C 2 '(PHYDM|phydm|halrf|halhwi...
```

**Output:**

```
275-
276-ccflags-y += -I$(src)/hal/btc
277:ccflags-y += -I$(src)/hal/phydm
278-
279-########### HAL_RTL8188E #################################
--
2353-
2354-########### this part for *.mk ############################
2355:include $(src)/hal/phydm/phydm.mk
2356-
2357-########### HAL_RTL8822B #################################
--
2446-$(MODULE_NAME)-y += $(_OS_INTFS_FILES)
24 
```

### 12:43:38  terminal

**Query:**

```
rg -n -C 2 '^(void|u8|u32|s32|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_phycfg.c-260- * */
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_phycfg.c-261-
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_phycfg.c:262:s32 PHY_MACConfig8192E(PADAPTER Adapter)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/rtl8192e_phycfg.c-263-{
/opt/data/repos/rtl8192eu- 
```

### 12:43:38  terminal

**Query:**

```
rg -n -C 2 '^(void|u8|u32|s32|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-18-
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-19-/* A mapping from HalData to ODM. */
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c:20:static enum odm_board_type boardType(u8 InterfaceSel)
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-21-{
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-22- 
```

### 12:43:38  terminal

**Query:**

```
rg -n -C 2 '^(void|u8|u32|s32|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-8179-#endif /* CONFIG_AP_WOWLAN */
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-8180-
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c:8181:static int rtw_pm_set(struct net_device *dev,
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-8182-		 struct  
```

### 12:43:38  terminal

**Query:**

```
rg -n -C 2 '^(static )?(int|void|u8|s...
```

**Output:**

```
1060-}
1061-
1062:void rtw_cfg80211_indicate_connect(_adapter *padapter)
1063-{
1064-	struct mlme_priv *pmlmepriv = &padapter->mlmepriv;
--
1196-}
1197-
1198:void rtw_cfg80211_indicate_disconnect(_adapter *padapter, u16 reason, u8 locally_generated)
1199-{
1200-	struct wireless_dev *pwdev = padapter->rtw_wdev;
--
1275-
1276-#ifdef CONFIG_AP_MODE
1277:static int rtw_cfg8 
```

### 12:43:38  terminal

**Query:**

```
rg -n -C 2 '^(int|u8|void|s32|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7206-}
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7207-
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c:7208:static int rtw_add_sta(struct net_device *dev, struct ieee_param *param)
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7209-{
/opt/data/ 
```

### 12:44:48  terminal

**Query:**

```
rg -n -C 3 '(USB_AggModeSwitch|dynami...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_com.c-14154-	u8 cur_wireless_mode = WIRELESS_INVALID;
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_com.c-14155-
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_com.c-14156-#ifdef CONFIG_USB_RX_AGGREGATION
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_com.c:14157:	if (!registry_par->dynamic_agg_enable)
/opt/data/repos/rt 
```

### 12:44:48  terminal

**Query:**

```
rg -n -C 3 '(rtw_tx_pwr_by_rate|rtw_t...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/include/hal_com.h-626-#endif
/opt/data/repos/rtl8192eu-advanced/driver/include/hal_com.h-627-
/opt/data/repos/rtl8192eu-advanced/driver/include/hal_com.h-628-#ifdef CONFIG_LOAD_PHY_PARA_FROM_FILE
/opt/data/repos/rtl8192eu-advanced/driver/include/hal_com.h:629:	extern char *rtw_phy_file_path;
/opt/data/repos/rtl8192eu-advanced/driver/includ 
```

### 12:44:48  terminal

**Query:**

```
rg -n -C 3 '(CONFIG_FILE_FWIMG|CONFIG...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/Makefile-58-CONFIG_POWER_SAVING = y
/opt/data/repos/rtl8192eu-advanced/driver/Makefile-59-CONFIG_IPS_MODE = default
/opt/data/repos/rtl8192eu-advanced/driver/Makefile-60-CONFIG_LPS_MODE = default
/opt/data/repos/rtl8192eu-advanced/driver/Makefile:61:CONFIG_USB_AUTOSUSPEND = n
/opt/data/repos/rtl8192eu-advanced/driver/Makefile-62-CONFIG_HW_P 
```

### 12:48:07  terminal

**Query:**

```
git -C /opt/data/repos/rtl8192eu-adva...
```

**Output:**

```
M driver/os_dep/linux/ioctl_cfg80211.c

--- branch ---
main

--- recent history ---
dbd4276 (HEAD -> main, origin/main) build: -Wno-error in the active CONFIG_RTL8192E branch
691aac1 fix: probe breadcrumbs use dev_dbg/netdev_dbg, not pr_debug
c0b6aa7 docs: Windows rtwlanu.sys first-pass analysis (Ghidra)
9460da1 release: v5.11.2.1-adv1 - production layout
d3a5556 debug: dyndb 
```

### 12:48:07  terminal

**Query:**

```
git -C /opt/data/repos/rtl8192eu-adva...
```

**Output:**

```
driver/os_dep/linux/ioctl_cfg80211.c | 21 +++++++++++++++++++--
 1 file changed, 19 insertions(+), 2 deletions(-)
diff --git a/driver/os_dep/linux/ioctl_cfg80211.c b/driver/os_dep/linux/ioctl_cfg80211.c
index 8f72ba3..8ea6184 100755
--- a/driver/os_dep/linux/ioctl_cfg80211.c
+++ b/driver/os_dep/linux/ioctl_cfg80211.c
@@ -16,6 +16,7 @@
 
 #include <drv_types.h>
 #include <hal_d 
```

### 12:48:07  terminal

**Query:**

```
rg -n -C 3 '(rtw_drv_proc_init|rtw_dr...
```

**Output:**

```
68-}
69-#endif
70-
71:inline struct proc_dir_entry *rtw_proc_create_dir(const char *name, struct proc_dir_entry *parent, void *data)
72-{
73-	struct proc_dir_entry *entry;
74-
--
84-	return entry;
85-}
86-
87:inline struct proc_dir_entry *rtw_proc_create_entry(const char *name, struct proc_dir_entry *parent,
88-#if (LINUX_VERSION_CODE >= KERNEL_VERSION(5,6,0))
89-	const 
```

### 12:48:07  terminal

**Query:**

```
rg -n -C 3 '(rtw_hal_dm_init|rtw_hal_...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-1240-#endif /* CONFIG_LPS_PG */
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-1241-}
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-1242-
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c:1243:void rtw_phydm_watchdog_in_lps_lclk(_adapter *adapter)
/opt/data/repos/rtl8192eu-advanced/driver/hal/hal_dm.c-1244 
```

### 12:48:55  terminal

**Query:**

```
rg -n -C 2 '^(static )?(u32|u8|s32|in...
```

**Output:**

```
24-};
25-
26:int usbctrl_vendorreq(struct intf_hdl *pintfhdl, u8 request, u16 value, u16 index, void *pdata, u16 len, u8 requesttype)
27-{
28-	_adapter	*padapter = pintfhdl->padapter;
--
395-}
396-#endif
397:void usb_read_mem(struct intf_hdl *pintfhdl, u32 addr, u32 cnt, u8 *rmem)
398-{
399-
400-}
401-
402:void usb_write_mem(struct intf_hdl *pintfhdl, u32 addr, u32 cnt,  
```

### 12:49:12  terminal

**Query:**

```
rg -n -C 2 '^(static )?(int|void|s32|...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_mlme.c-4036-}
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_mlme.c-4037-
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_mlme.c:4038:void rtw_dynamic_check_timer_handlder(void *ctx)
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_mlme.c-4039-{
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_mlme.c-4040-	struct dvobj_ 
```

### 12:49:31  terminal

**Query:**

```
rg -n -C 2 '^(s32|int|u8|void|static ...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-1734-}
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-1735-
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c:1736:void rtl8192eu_set_hal_ops(_adapter *padapter)
/opt/data/repos/rtl8192eu-advanced/driver/hal/rtl8192e/usb/usb_halinit.c-1737-{
/opt/data/repos/rtl8 
```

### 12:49:34  terminal

**Query:**

```
rg -n -C 2 '(rtw_cfg80211_(init|unini...
```

**Output:**

```
9739-
9740-#ifdef CONFIG_80211N_HT
9741:static void rtw_cfg80211_init_ht_capab_ex(_adapter *padapter
9742-	, struct ieee80211_sta_ht_cap *ht_cap, BAND_TYPE band, u8 rf_type)
9743-{
--
9788-}
9789-
9790:static void rtw_cfg80211_init_ht_capab(_adapter *padapter
9791-	, struct ieee80211_sta_ht_cap *ht_cap, BAND_TYPE band, u8 rf_type)
9792-{
--
9814-	}
9815-
9816:	rtw_cfg 
```

### 12:50:25  terminal

**Query:**

```
rg -n -C 2 '(rtw_cfg80211_ndev_res_al...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/os_intfs.c-1957-
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/os_intfs.c-1958-#if defined(CONFIG_IOCTL_CFG80211)
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/os_intfs.c:1959:	if (rtw_cfg80211_ndev_res_alloc(adapter) != _SUCCESS) {
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/os_intfs.c-1960-		rtw 
```

### 12:50:36  terminal

**Query:**

```
rg -n -C 2 '(hostapd_mode_(init|unloa...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7187-}
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7188-
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c:7189:static int rtw_hostapd_sta_flush(struct net_device *dev)
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/ioctl_linux.c-7190-{
/opt/data/repos/rtl8192eu- 
```

### 12:50:36  terminal

**Query:**

```
rg -n -C 2 '(rtw_hal_init\(|intf_star...
```

**Output:**

```
880-#endif
881-
882:int _netdev_open(struct net_device *pnetdev);
883:int netdev_open(struct net_device *pnetdev);
884-static int netdev_close(struct net_device *pnetdev);
885-#ifdef CONFIG_PLATFORM_INTEL_BYT
--
1807-	.ndo_init = rtw_ndev_init,
1808-	.ndo_uninit = rtw_ndev_uninit,
1809:	.ndo_open = netdev_open,
1810-	.ndo_stop = netdev_close,
1811-	.ndo_start_xmit = rtw 
```

### 12:52:01  terminal

**Query:**

```
rg -n -C 2 '(tx_power_offset|power_of...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_debug.c-2172-
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_debug.c-2173-
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_debug.c:2174:int proc_get_tx_power_offset(struct seq_file *m, void *v)
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_debug.c-2175-{
/opt/data/repos/rtl8192eu-advanced/driver/core/rtw_debug.c-2176-	 
```

### 12:52:02  terminal

**Query:**

```
rg -n -C 2 '(proc_set_write_reg|proc_...
```

**Output:**

```
2559-}
2560-
2561:static ssize_t proc_set_tpc_settings(struct file *file, const char __user *buffer, size_t count, loff_t *pos, void *data)
2562-{
2563-	struct net_device *dev = data;
--
2826-}
2827-
2828:static ssize_t proc_set_kfree_flag(struct file *file, const char __user *buffer, size_t count, loff_t *pos, void *data)
2829-{
2830-	struct net_device *dev = data;
--
28 
```

### 12:52:08  terminal

**Query:**

```
rg -n -C 2 '(rtw_hal_set_tx_power_lev...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_antdiv.c-1857-	((PADAPTER)adapter)->HalFunc.SetTxPowerLevelHandler(adapter, *dm->channel);
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_antdiv.c-1858-#elif (DM_ODM_SUPPORT_TYPE == ODM_CE)
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_antdiv.c:1859:	rtw_hal_set_tx_power_level(adapter, *dm->channel);
 
```

### 12:52:11  terminal

**Query:**

```
rg -n -C 2 '(CONFIG_RTL8192E|RTL8192E...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_cck_pd.h-42-/*@Run time flag of CCK_PD HW type*/
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_cck_pd.h-43-#define CCK_PD_IC_TYPE1 (ODM_RTL8188E | ODM_RTL8812 | ODM_RTL8821 |\
/opt/data/repos/rtl8192eu-advanced/driver/hal/phydm/phydm_cck_pd.h:44:			ODM_RTL8192E | ODM_RTL8723B | ODM_RTL8814A |\
/opt/data/repos 
```

### 12:52:30  terminal

**Query:**

```
rg -n -C 3 'static ssize_t proc_set_(...
```

**Output:**

```
2558-	return 0;
2559-}
2560-
2561:static ssize_t proc_set_tpc_settings(struct file *file, const char __user *buffer, size_t count, loff_t *pos, void *data)
2562-{
2563-	struct net_device *dev = data;
2564-	_adapter *adapter = (_adapter *)rtw_netdev_priv(dev);
--
2825-	return 0;
2826-}
2827-
2828:static ssize_t proc_set_kfree_flag(struct file *file, const char __user *buf 
```

### 12:52:34  terminal

**Query:**

```
rg -n -C 2 '(rtw_proc_create_entry|pr...
```

**Output:**

```
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/rtw_proc.c-74-
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/rtw_proc.c-75-#if (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 10, 0))
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/rtw_proc.c:76:	entry = proc_mkdir_data(name, S_IRUGO | S_IXUGO, parent, data);
/opt/data/repos/rtl8192eu-advanced/driver/os_dep/linux/rtw 
```

### 13:01:20  terminal

**Query:**

```
printf '%s\n' '--- status ---' + 9 co...
```

**Output:**

```
--- status ---
 M driver/os_dep/linux/ioctl_cfg80211.c
--- branch ---
main
--- head ---
dbd42766d00f9c3c5a4d7da9c913642ca63f33a1
--- history ---
dbd4276 2026-10-20 build: -Wno-error in the active CONFIG_RTL8192E branch
691aac1 2026-10-20 fix: probe breadcrumbs use dev_dbg/netdev_dbg, not pr_debug
c0b6aa7 2026-10-19 docs: Windows rtwlanu.sys first-pass analysis (Ghidra)
9460da 
```

### 13:01:20  terminal

**Query:**

```
printf '%s\n' '--- tracked driver sou...
```

**Output:**

```
--- tracked driver source counts ---
 1 Kconfig
 1 Makefile
 1 README.md
 1 clean
 77 core
 1 dkms.conf
 196 hal
 1 ifcfg-wlan0
 267 include
 1 install_wifi.sh
 26 os_dep
 17 platform
 1 runwpa
 1 uninstall_wifi.sh
 1 wlan0dhcp
--- top-level driver layout ---
driver
driver/core
driver/core/crypto
driver/core/efuse
driver/core/mesh
driver/core/monitor
driver/core/ 
```

### 13:01:21  terminal

**Query:**

```
git log --all --oneline --decorate --...
```

**Output:**

```
82c6b22 feat: wire the tx_power_offset proc knob into the TX power target
123b345 driver: import Realtek official 5.11.2.1 base tree
--- recent driver diffs vs parent ---
dbd4276 build: -Wno-error in the active CONFIG_RTL8192E branch
 driver/Makefile | 20 ++++----------------
 1 file changed, 4 insertions(+), 16 deletions(-)
```

### 13:01:43  terminal

**Query:**

```
git diff --no-ext-diff --unified=80 -...
```

**Output:**

```
diff --git a/driver/os_dep/linux/ioctl_cfg80211.c b/driver/os_dep/linux/ioctl_cfg80211.c
index 8f72ba3..8ea6184 100755
--- a/driver/os_dep/linux/ioctl_cfg80211.c
+++ b/driver/os_dep/linux/ioctl_cfg80211.c
@@ -1,98 +1,99 @@
 /******************************************************************************
 *
 * Copyright(c) 2007 - 2019 Realtek Corporation.
 *
 * This program is f 
```

### 13:01:43  terminal

**Query:**

```
git show --format=fuller --stat 85639...
```

**Output:**

```
commit 85639a8f4f1a1c85cef412b6907d30db14b87db8
Author: thenabbu <128571614+thenabbu@users.noreply.github.com>
AuthorDate: Mon Oct 19 19:32:05 2026 +0000
Commit: thenabbu <128571614+thenabbu@users.noreply.github.com>
CommitDate: Mon Oct 19 19:32:05 2026 +0000

 feat: enable CONFIG_WIFI_MONITOR (monitor mode)
 
 Official stock ships monitor mode compiled out.

 driver/Makefile 
```

### 13:01:43  terminal

**Query:**

```
git show --format= --name-only 85639a...
```

**Output:**

```
driver/Makefile
-- injection --
driver/core/rtw_xmit.c
driver/include/drv_conf.h
-- power-offset --
driver/hal/hal_com_phycfg.c
-- PM --
driver/os_dep/linux/usb_intf.c
```

### 13:03:17  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32) (...
```

**Output:**

```
882:int _netdev_open(struct net_device *pnetdev);
1971:void rtw_os_ndev_free(_adapter *adapter)
2099:static int rtw_os_ndev_register(_adapter *adapter, const char *name)
2787:u8 rtw_init_drv_sw(_adapter *padapter)
3069:u8 rtw_free_drv_sw(_adapter *padapter)
3718:void rtw_os_ndevs_unregister(struct dvobj_priv *dvobj)
3744:int rtw_os_ndevs_init(struct dvobj_priv *dvobj)
3817:int _ 
```

### 13:03:17  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32) (...
```

**Output:**

```
{"output": "driver/hal/rtl8192e/usb/usb_halinit.c:93:static void rtl8192eu_interface_configure(_adapter *padapter)\ndriver/hal/rtl8192e/rtl8192e_dm.c:288:void rtl8192e_init_dm_priv(PADAPTER Adapter)\ndriver/hal/rtl8192e/rtl8192e_hal_init.c:4531:void rtl8192e_init_default_value(_adapter *padapter)\n--- functions in phycfg ---\n262:s32 PHY_MACConfig8192E(PADAPTER Adapter)", "exit_code": 0, "error":  …(+5 chars)
```

### 13:03:17  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32|u3...
```

**Output:**

```
26:int usbctrl_vendorreq(struct intf_hdl *pintfhdl, u8 request, u16 value, u16 index, void *pdata, u16 len, u8 requesttype)
408:void usb_read_port_cancel(struct intf_hdl *pintfhdl)
431:static void usb_write_port_complete(struct urb *purb, struct pt_regs *regs)
566:u32 usb_write_port(struct intf_hdl *pintfhdl, u32 addr, u32 cnt, u8 *wmem)
703:void usb_write_port_cancel(struct intf_h 
```

### 13:03:17  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32|u3...
```

**Output:**

```
driver/hal/rtl8192e/usb/rtl8192eu_recv.c:25:void rtl8192eu_free_recv_priv(_adapter *padapter)
driver/core/rtw_recv.c:2860:static int rtw_recv_indicatepkt_check(union recv_frame *rframe, u8 *ehdr_pos, u32 pkt_len)
driver/core/rtw_recv.c:4318:s32 rtw_recv_entry(union recv_frame *precvframe)
driver/os_dep/linux/recv_linux.c:424:void rtw_os_recv_indicate_pkt(_adapter *padapter, _pkt *pk 
```

### 13:03:18  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32) (...
```

**Output:**

```
driver/os_dep/linux/os_intfs.c:4144:int rtw_ips_pwr_up(_adapter *padapter)
driver/os_dep/linux/os_intfs.c:4172:void rtw_ips_pwr_down(_adapter *padapter)
driver/core/rtw_pwrctrl.c:273:void rtw_ps_processor(_adapter *padapter)
driver/core/rtw_pwrctrl.c:933:void rtw_set_ps_mode(PADAPTER padapter, u8 ps_mode, u8 smart_ps, u8 bcn_ant_mode, const char *msg)
driver/core/rtw_pwrctrl.c:1369 
```

### 13:03:18  terminal

**Query:**

```
rg -n '^(static )?(int|void|u8|s32) (...
```

**Output:**

```
2289:static int cfg80211_rtw_set_default_key(struct wiphy *wiphy, struct net_device *ndev, 
3165:static int cfg80211_rtw_scan(struct wiphy *wiphy
4263:static int cfg80211_rtw_connect(struct wiphy *wiphy, struct net_device *ndev,
4527:static int cfg80211_rtw_disconnect(struct wiphy *wiphy, struct net_device *ndev,
5352:static int cfg80211_rtw_start_ap(struct wiphy *wiphy, struct net 
```

### 13:04:19  terminal

**Query:**

```
rg -n -C 2 '(CONFIG_IOCTL_CFG80211|CO...
```

**Output:**

```
53-CONFIG_GSPI_HCI = n
54-########################## Features ###########################
55:CONFIG_AP_MODE = y
56-CONFIG_P2P = y
57:CONFIG_MP_INCLUDED = y
58:CONFIG_POWER_SAVING = y
59-CONFIG_IPS_MODE = default
60-CONFIG_LPS_MODE = default
61-CONFIG_USB_AUTOSUSPEND = n
62-CONFIG_HW_PWRP_DETECTION = n
63:CONFIG_BT_COEXIST = y
64-CONFIG_WAPI_SUPPORT = n
65-CONFIG_EFUSE_CONFI 
```

### 13:04:19  terminal

**Query:**

```
rg -n -C 2 '^(static )?(int|u8|void|s...
```

**Output:**

```
driver/hal/rtl8192e/usb/usb_halinit.c-663-	return value;
driver/hal/rtl8192e/usb/usb_halinit.c-664-}
driver/hal/rtl8192e/usb/usb_halinit.c:665:static u32 rtl8192eu_hal_init(PADAPTER Adapter)
driver/hal/rtl8192e/usb/usb_halinit.c-666-{
driver/hal/rtl8192e/usb/usb_halinit.c-667-	u8	value8 = 0;
--
driver/hal/rtl8192e/usb/usb_halinit.c-834-	HAL_INIT_PROFILE_TAG(HAL_INIT_STAGES_DO 
```

### 13:04:20  terminal

**Query:**

```
rg -n -C 2 '^(static )?(int|u8|void|s...
```

**Output:**

```
driver/os_dep/linux/os_intfs.c-2392-}
driver/os_dep/linux/os_intfs.c-2393-
driver/os_dep/linux/os_intfs.c:2394:void rtw_stop_drv_threads(_adapter *padapter)
driver/os_dep/linux/os_intfs.c-2395-{
driver/os_dep/linux/os_intfs.c-2396-	RTW_INFO(FUNC_ADPT_FMT" enter\n", FUNC_ADPT_ARG(padapter));
--
driver/hal/hal_intf.c-469-
driver/hal/hal_intf.c-470-
driver/hal/hal_intf.c:471:s 
```

### 13:04:20  terminal

**Query:**

```
rg -n -C 2 'rtw_dynamic_check_timer_h...
```

**Output:**

```
driver/core/rtw_sreset.c-266-
driver/core/rtw_sreset.c-267-	if (is_primary_adapter(padapter))
driver/core/rtw_sreset.c:268:		_set_timer(&adapter_to_dvobj(padapter)->dynamic_chk_timer, 2000);
driver/core/rtw_sreset.c-269-
driver/core/rtw_sreset.c-270-	rtw_netif_wake_queue(padapter->pnetdev);
--
driver/core/rtw_mlme.c-2618-		rtw_set_ips_deny(padapter, 0);
driver/core/rtw_mlm 
```

### 13:04:20  terminal

**Query:**

```
rg -n -C 2 '(rtw_set_monitor_mode|rtw...
```

**Output:**

```
driver/os_dep/linux/ioctl_linux.c-1388-#ifdef CONFIG_WIFI_MONITOR
driver/os_dep/linux/ioctl_linux.c-1389-	case IW_MODE_MONITOR:
driver/os_dep/linux/ioctl_linux.c:1390:		networkType = Ndis802_11Monitor;
driver/os_dep/linux/ioctl_linux.c-1391-
driver/os_dep/linux/ioctl_linux.c-1392-		rtw_ps_deny(padapter, PS_DENY_MONITOR_MODE);
--
driver/os_dep/linux/ioctl_linux.c-1398-
drive 
```

### 13:04:21  terminal

**Query:**

```
git show --format= --unified=80 7d9ea...
```

**Output:**

```
diff --git a/driver/core/rtw_xmit.c b/driver/core/rtw_xmit.c
index f2ccf7e..4e5da4f 100755
--- a/driver/core/rtw_xmit.c
+++ b/driver/core/rtw_xmit.c
@@ -4661,203 +4661,210 @@ u32 rtw_get_ff_hwaddr(struct xmit_frame *pxmitframe)
 
 	return addr;
 
 }
 
 static void do_queue_select(_adapter	*padapter, struct pkt_attrib *pattrib)
 {
 	u8 qsel;
 
 	qsel = pattrib->priorit 
```

### 13:06:20  execute_code

**Query:**

```
from hermes_tools import terminal imp...
```

**Output:**

```
rtw_la_mode_en	31	3	0	
rtw_wireless_mode	37	4	0	
rtw_nb_config	91	12	6	driver/include/drv_types.h:246:	u8	rtw_nb_config;|driver/hal/hal_dm.c:473:	if ((adapter->registrypriv.rtw_nb_config == RTW_NB_CONFIG_WIDTH_10)|driver/hal/hal_dm.c:474:		|| (adapter->registrypriv.rtw_nb_config == RTW_NB_CONFIG_WIDTH_5)) {|driver/hal/hal_dm.c:475:		odm_cmn_inf 
```

### 13:06:42  execute_code

**Query:**

```
from hermes_tools import terminal r=t...
```

**Output:**

```
{"status": "success", "output": "rtw_fw_mp_bt_file_path\tdecl=634\tuses=1\tdriver/os_dep/linux/os_intfs.c:633:char *rtw_fw_mp_bt_file_path = \"\";\n", "exit_code": 0, "tool_calls_made": 1, "duration_seconds": 10.63, "kernel": {"mode": "session", "reused": true, "execution_count": 2, "state_reset": false}, "stdout_truncated": false, "stdout_bytes_captured": 109, "stdout_bytes_total": 109, "stdout_b …(+17 chars)
```

### 13:06:55  terminal

**Query:**

```
rg -n -C 3 'rtw_regsty_load_.*\(|load...
```

**Output:**

```
1022-#endif
1023-
1024-#if CONFIG_TX_AC_LIFETIME
1025:static void rtw_regsty_load_tx_ac_lifetime(struct registry_priv *regsty)
1026-{
1027-	int i, j;
1028-	struct tx_aclt_conf_t *conf;
--
1056-}
1057-#endif
1058-
1059:static void rtw_regsty_load_target_tx_power(struct registry_priv *regsty)
1060-{
1061-	int path, rs;
1062-	int *target_tx_pwr;
--
1092-#endif /* CONFI 
```

### 13:06:55  terminal

**Query:**

```
rg -n -C 2 '(rtw_phydm_ability|rtw_ha...
```

**Output:**

```
driver/hal/hal_dm.c-166-	LeaveAllPowerSaveModeDirect(adapter);
driver/hal/hal_dm.c-167-
driver/hal/hal_dm.c:168:	rtw_phydm_ability_backup(adapter);
driver/hal/hal_dm.c-169-	rtw_phydm_func_disable_all(adapter);
driver/hal/hal_dm.c-170-
--
driver/hal/hal_dm.c-172-
driver/hal/hal_dm.c-173-	rtw_phydm_iqk_trigger_dbg(adapter, recovery, clear, segment);
driver/hal/hal_dm.c:174:	 
```

### 13:06:56  terminal

**Query:**

```
rg -n -C 2 '(en_napi|en_gro|napi_thre...
```

**Output:**

```
driver/hal/hal_com.c-14155-
driver/hal/hal_com.c-14156-#ifdef CONFIG_USB_RX_AGGREGATION
driver/hal/hal_com.c:14157:	if (!registry_par->dynamic_agg_enable)
driver/hal/hal_com.c-14158-		return;
driver/hal/hal_com.c-14159-
--
driver/hal/rtl8192e/usb/usb_halinit.c-110-#ifdef CONFIG_USB_RX_AGGREGATION
driver/hal/rtl8192e/usb/usb_halinit.c-111-
driver/hal/rtl8192e/usb/usb_halinit. 
```

### 13:06:56  terminal

**Query:**

```
rg -n -C 2 '(load_phy_file|decrypt_ph...
```

**Output:**

```
driver/core/rtw_debug.c-100-#endif
driver/core/rtw_debug.c-101-
driver/core/rtw_debug.c:102:#ifdef CONFIG_LOAD_PHY_PARA_FROM_FILE
driver/core/rtw_debug.c-103-	RTW_PRINT_SEL(sel, "LOAD_PHY_PARA_FROM_FILE - REALTEK_CONFIG_PATH=%s\n", REALTEK_CONFIG_PATH);
driver/core/rtw_debug.c-104-	#if defined(CONFIG_MULTIDRV) || defined(REALTEK_CONFIG_PATH_WITH_IC_NAME_FOLDER)
--
driver/hal 
```

### 13:12:42  execute_code

**Query:**

```
from hermes_tools import terminal r=t...
```

**Output:**

```
PARAM_COUNT 178
rtw_la_mode_en	31	30,1276	2
rtw_wireless_mode	37	36,1165,1167	3
rtw_nb_config	91	90,1164,1248,1279	4
rtw_ips_mode	95	47,79,1192	3
rtw_lps_level	98	55,57,61,81,1194	5
rtw_lps_1t1r	103	102,1198	2
rtw_lps_chk_by_tp	107	64,82,1200	3
rtw_wow_power_mgnt	110	70,73,84,1202	4
rtw_wow_lps_level	112	71,74,85,1203	4
rtw_wow_ 
```

### 13:13:07  terminal

**Query:**

```
rg -n -C 2 '(rtw_fw_file_path|rtw_fw_...
```

**Output:**

```
driver/include/rtl8710b_hal.h-195-
driver/include/rtl8710b_hal.h-196-#ifdef CONFIG_FILE_FWIMG
driver/include/rtl8710b_hal.h:197:	extern char *rtw_fw_file_path;
driver/include/rtl8710b_hal.h:198:	extern char *rtw_fw_wow_file_path;
driver/include/rtl8710b_hal.h-199-	#ifdef CONFIG_MP_INCLUDED
driver/include/rtl8710b_hal.h:200:		extern char *rtw_fw_mp_bt_file_path;
driver/includ 
```

### 13:13:07  terminal

**Query:**

```
rg -n -C 2 '(rtw_initmac|rtw_enusbss)...
```

**Output:**

```
driver/core/rtw_ieee80211.c-1715-}
driver/core/rtw_ieee80211.c-1716-
driver/core/rtw_ieee80211.c:1717:extern char *rtw_initmac;
driver/core/rtw_ieee80211.c-1718-/**
driver/core/rtw_ieee80211.c-1719- * rtw_macaddr_cfg - Decide the mac address used
--
driver/core/rtw_ieee80211.c-1732-
driver/core/rtw_ieee80211.c-1733-	/* Users specify the mac address */
driver/core/rtw_ieee80211 
```

### 13:13:08  terminal

**Query:**

```
rg -n -C 2 '(initmac|enusbss)' driver...
```

**Output:**

```
driver/core/rtw_ieee80211.c-1715-}
driver/core/rtw_ieee80211.c-1716-
driver/core/rtw_ieee80211.c:1717:extern char *rtw_initmac;
driver/core/rtw_ieee80211.c-1718-/**
driver/core/rtw_ieee80211.c-1719- * rtw_macaddr_cfg - Decide the mac address used
--
driver/core/rtw_ieee80211.c-1732-
driver/core/rtw_ieee80211.c-1733-	/* Users specify the mac address */
driver/core/rtw_ieee80211 
```

### 13:13:08  terminal

**Query:**

```
rg -n -C 2 '(proc_set_(write|read)_re...
```

**Output:**

```
driver/core/rtw_debug.c-970-}
driver/core/rtw_debug.c-971-
driver/core/rtw_debug.c:972:ssize_t proc_set_write_reg(struct file *file, const char __user *buffer, size_t count, loff_t *pos, void *data)
driver/core/rtw_debug.c-973-{
driver/core/rtw_debug.c-974-	struct net_device *dev = data;
--
driver/core/rtw_debug.c-992-
driver/core/rtw_debug.c-993-		if (num != 3) {
driver/cor 
```

### 13:13:08  terminal

**Query:**

```
nl -ba driver/os_dep/linux/rtw_proc.c...
```

**Output:**

```
5100	#if defined(DBG_CONFIG_ERROR_DETECT)
 5101		RTW_PROC_HDL_SSEQ("sreset", proc_get_sreset, proc_set_sreset),
 5102	#endif /* DBG_CONFIG_ERROR_DETECT */
 5103		RTW_PROC_HDL_SSEQ("trx_info_debug", proc_get_trx_info_debug, NULL),
 5104	
 5105	#ifdef CONFIG_HUAWEI_PROC
 5106		RTW_PROC_HDL_SSEQ("huawei_trx_info", proc_get_huawei_trx_info, NULL),
 5107	#endif
 510 
```

### 13:13:08  terminal

**Query:**

```
git status --porcelain + 3 commands
```

**Output:**

```
M driver/os_dep/linux/ioctl_cfg80211.c
21	2	driver/os_dep/linux/ioctl_cfg80211.c
diff --git a/driver/os_dep/linux/ioctl_cfg80211.c b/driver/os_dep/linux/ioctl_cfg80211.c
index 8f72ba3..71fbba8 100755
--- a/driver/os_dep/linux/ioctl_cfg80211.c
+++ b/driver/os_dep/linux/ioctl_cfg80211.c
@@ -16,6 +16,7 @@
 
 #include <drv_types.h>
 #include <hal_data.h>
+#include <generated/ut 
```

### 13:17:03  terminal

**Query:**

```
rg -n '(CONFIG_RTW_NAPI|CONFIG_RTW_GR...
```

**Output:**

```
51:CONFIG_PCI_HCI = n
55:CONFIG_AP_MODE = y
57:CONFIG_MP_INCLUDED = y
58:CONFIG_POWER_SAVING = y
59:CONFIG_IPS_MODE = default
60:CONFIG_LPS_MODE = default
63:CONFIG_BT_COEXIST = y
68:CONFIG_LOAD_PHY_PARA_FROM_FILE = y
71:CONFIG_TXPWR_LIMIT = y
72:CONFIG_TXPWR_LIMIT_EN = n
80:CONFIG_TDLS = n
81:CONFIG_WIFI_MONITOR = y
82:CONFIG_MCC_MODE = n
84:CONFIG_RTW_NAPI = y
85:CONFIG 
```

### 13:17:03  terminal

**Query:**

```
rg -n 'monitor' driver/include/autoco...
```

**Output:**

```
driver/Makefile:2392:		core/monitor/rtw_radiotap.o \
--- xmit entry monitor ---
1396-	if(pattrib->icmp_pkt==1)/*use VO queue to send icmp packet*/
1397-		UserPriority = 7;
1398-	#endif
1399:	#ifdef CONFIG_IP_R_MONITOR
1400-	if (pattrib->ether_type == ETH_P_ARP)
1401-		UserPriority = 7;
1402:	#endif/*CONFIG_IP_R_MONITOR*/
1403-
1404-null_pkt:
1405-	pattrib->prior 
```

### 13:25:52  terminal

**Query:**

```
rg -n '(power_offset)' driver --glob ...
```

**Output:**

```
driver/include/drv_types.h:1785:	u8 power_offset;
driver/include/rtw_debug.h:360:ssize_t proc_set_tx_power_offset(struct file *file, const char __user *buffer, size_t count, loff_t *pos, void *data);
driver/include/rtw_debug.h:361:int proc_get_tx_power_offset(struct seq_file *m, void *v);
driver/core/rtw_debug.c:2174:int proc_get_tx_power_offset(struct seq_file *m, void *v)
driver 
```

### 13:25:53  terminal

**Query:**

```
rg -n '(rtw_proc_create_entry|rtw_pro...
```

**Output:**

```
driver/os_dep/linux/rtw_proc.c:71:inline struct proc_dir_entry *rtw_proc_create_dir(const char *name, struct proc_dir_entry *parent, void *data)
driver/os_dep/linux/rtw_proc.c:87:inline struct proc_dir_entry *rtw_proc_create_entry(const char *name, struct proc_dir_entry *parent,
driver/os_dep/linux/rtw_proc.c:328:	rtw_proc = rtw_proc_create_dir(RTW_PROC_NAME, get_proc_net, NULL);
d 
```

### 13:25:53  terminal

**Query:**

```
rg -n '(usb_intf_start|usb_intf_stop|...
```

**Output:**

```
93:static void rtl8192eu_interface_configure(_adapter *padapter)
100:		pHalData->UsbBulkOutSize = USB_HIGH_SPEED_BULK_SIZE;/* 512 bytes */
102:		pHalData->UsbBulkOutSize = USB_FULL_SPEED_BULK_SIZE;/* 64 bytes */
120:	/* pHalData->UsbRxAggPageCount	= 16; */ /* uint :128 b */ /* 0x0A;	 */ /* 10 = MAX_RX_DMA_BUFFER_SIZE/2/pHalData->UsbBulkOutSize */
172:	/* PlatformEFIOWrite2B 
```

### 13:25:53  terminal

**Query:**

```
rg -n '(rtw_dynamic_check_timer_handl...
```

**Output:**

```
driver/os_dep/linux/os_intfs.c:2621:	rtw_init_timer(&(pdvobj->dynamic_chk_timer), NULL, rtw_dynamic_check_timer_handlder, pdvobj);
driver/core/rtw_mlme.c:3913:		/* due to rtw_dynamic_check_timer_handlder() is called every 2 seconds */
driver/core/rtw_mlme.c:4038:void rtw_dynamic_check_timer_handlder(void *ctx)
--- ps anchors ---
driver/os_dep/linux/os_intfs.c:4144:int rtw_ips_pw 
```

### 13:25:54  terminal

**Query:**

```
rg -n '(nlrtw_init|nlrtw_deinit|nlrtw...
```

**Output:**

```
61:static int nlrtw_ch_util_set(struct sk_buff *skb, struct genl_info *info)
72:static struct nla_policy nlrtw_genl_policy[NUM_NLRTW_ATTR] = {
76:static struct genl_ops nlrtw_genl_ops[] = {
80:		.policy = nlrtw_genl_policy,
89:static struct genl_multicast_group nlrtw_genl_mcgrp[] = {
94:static struct genl_family nlrtw_genl_family = {
105:	.ops = nlrtw_genl_ops,
106:	.n_ops = 
```

### 13:25:54  terminal

**Query:**

```
rg -n '(CONFIG_XMIT_THREAD_MODE|CONFI...
```

**Output:**

```
driver/include/autoconf.h:84:	/* #define CONFIG_XMIT_THREAD_MODE */
driver/include/rtw_xmit.h:37:		#define NR_XMITBUFF	(16)
driver/include/rtw_xmit.h:41:		#define NR_XMITBUFF	(128)
driver/include/rtw_xmit.h:59:		#define NR_XMITBUFF	(1)
driver/include/rtw_xmit.h:61:		#define NR_XMITBUFF	(4)
driver/include/rtw_xmit.h:70:	#define NR_XMITBUFF	(256)
driver/include/rtw_x 
```

### 13:30:08  terminal

**Query:**

```
rg -n '(CONFIG_EMBEDDED_FWIMG|CONFIG_...
```

**Output:**

```
driver/include/rtl8192e_hal.h:65:#ifdef CONFIG_EMBEDDED_FWIMG
driver/include/autoconf.h:46:#define CONFIG_EMBEDDED_FWIMG
driver/include/autoconf.h:48:#ifdef CONFIG_EMBEDDED_FWIMG
driver/include/autoconf.h:51:/* #define CONFIG_FILE_FWIMG */
driver/hal/rtl8192e/rtl8192e_hal_init.c:381:#ifdef CONFIG_FILE_FWIMG
driver/hal/rtl8192e/rtl8192e_hal_init.c:405:#ifdef CONFIG_FILE_FWIMG
driv 
```

### 13:30:08  terminal

**Query:**

```
rg -n '(rtw_monitor_xmit_entry|rtw_nd...
```

**Output:**

```
driver/include/rtw_xmit.h:1002:s32 rtw_monitor_xmit_entry(struct sk_buff *skb, struct net_device *ndev);
driver/os_dep/linux/xmit_linux.c:532:			rtw_monitor_xmit_entry((struct sk_buff *)pkt, pnetdev);
driver/core/rtw_xmit.c:4710:s32 rtw_monitor_xmit_entry(struct sk_buff *skb, struct net_device *ndev)
--- drv_conf 7d9eab6 ---
 
 CONFIG_MONITOR_MODE_XMIT carries Realtek's own car 
```

### 13:30:08  terminal

**Query:**

```
nl -ba driver/os_dep/linux/rtw_proc.c...
```

**Output:**

```
60		ret = single_open(file, show, data);
 61		if (ret) {
 62			kfree(buf);
 63			return ret;
 64		}
 65		((struct seq_file *)file->private_data)->buf = buf;
 66		((struct seq_file *)file->private_data)->size = size;
 67		return 0;
 68	}
 69	#endif
 70	
 71	inline struct proc_dir_entry *rtw_proc_create_dir(const char *name, struct proc_dir_entry *parent, 
```

### 13:30:08  terminal

**Query:**

```
rg -n '^(int|u8|s32|void) (rtw_init_d...
```

**Output:**

```
driver/os_dep/linux/xmit_linux.c:516:int rtw_xmit_entry(_pkt *pkt, _nic_hdl pnetdev)
driver/os_dep/linux/os_intfs.c:883:int netdev_open(struct net_device *pnetdev);
driver/os_dep/linux/os_intfs.c:2787:u8 rtw_init_drv_sw(_adapter *padapter)
driver/os_dep/linux/os_intfs.c:3069:u8 rtw_free_drv_sw(_adapter *padapter)
driver/os_dep/linux/os_intfs.c:4063:int netdev_open(struct net_device 
```

