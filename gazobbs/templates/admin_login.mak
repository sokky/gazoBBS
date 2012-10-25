<%include file="header.mak"/>
<%!
	from gazobbs import conf
%>
<table width='100%'><tr><th bgcolor=#E08000>
<font color=#FFFFFF>管理モード</font>
</th></tr>
	<center>
		<a href="/${conf.SELF_NAME}">掲示板に戻る</a>
		<a href="/${conf.SELF_NAME}">ログを更新する</a>
	</center>
</table>
<p>
	<form action="/${conf.SELF_NAME}" method=POST>
	<center>
		<input type=radio name=admin value=del checked>記事削除 
		<input type=radio name=admin value=post>管理人投稿
<p>
		<input type=hidden name=mode value=admin>
		<input type=password name=pass size=8>
		<input type=submit value= 認証 >
	</center>
	</form>
</body>
</html>
