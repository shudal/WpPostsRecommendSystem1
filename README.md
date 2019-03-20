# 基于LightFM的Wordpress文章推荐系统

### 说明
   此系统记录用户游览过的文章，生成推荐文章到wordppres的_uermeta表的meta_key为_perci_haku_reco里。推荐文章的id以分隔符|分开。请自行查询用户的推荐文章并配置到主题文件里。

### 安装
* 安装/plugin/下插件。文件名为perci-post-reco.zip
* 在当前使用主题查看一篇文章的模板文件（如single.php里) 增加如下php代码:
```
<?php
// By Junhao. 记录用户阅读文章历史
do_action('perci_post_reco', ['userid' => wp_get_current_user()->ID, 'postid' => $post->ID]);
?>
```
* 配置/plugin/config.ini

| 参数 			| 值									|
| ------------- | ------------------------------------- |
| host			| 数据库地址							|
| port			| 数据库端口							|
| user			| wordpress的数据库的用户名 			|
| password		| wordpress的数据库用户的密码			|
| database		| wordpress的数据库名					|
| table_prefix 	| wordpress的数据库表前缀。如wp			|
* 安装完毕。

### 使用。
* python3环境下运行/py/p.py 。需要的第三方库有：
```
1. configparser
2. pymysql
3. numpy
4. lightfm
```
* 这样就生成了推荐文章。之后请自行获得用户的推荐文章并进一步配置到主题文件中。
```
一种可能的推荐文章栏目对应的分类模板文件里的一些代码。category-35.php:
<?php
			$recoposts2 = get_usermeta(wp_get_current_user()->ID, '_perci_haku_reco');
            $recoposts2 = substr($recoposts2, 1);
            $recoposts = explode("|", $recoposts2);
            
            global $posts;
            
			$rposts = [];
			if (count($recoposts)) {
				for($i=0; $i<count($recoposts); $i++) {
					$rposts[] = get_post((int)$recoposts[$i]);
				}
			}

			$posts = $rposts;
?>
这样就将The Loop中的文章列表替换为推荐文章列表
```
