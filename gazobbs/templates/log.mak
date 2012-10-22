<%include file="header.mak"/>
<%include file="form.mak"/>
<%!
	from gazobbs import conf
	import myfilters as fil
%>

% for log in logs:

% if not log['pict'] == '':
画像タイトル：${log['pict'] | n}
% endif
<form action="/userdel" method="POST">
<input type="checkbox" name="${log['no']}" value="delete">
<font color="#cc1105" size=+1><b>${log['sub']}</b></font>
Name <font color="#117743"><b>${(log['name'], log['email']) | fil.email_link, n}</b></font>
${log['now']} No.${log['no']} &nbsp;
% if res == 0: 
	<a href="/${conf.SELF_NAME}/res/${log['no']}">返信</a>
% endif
<blockquote>${log['com'] | fil.auto_link, fil.comment_fix, n}</blockquote>
% if log['del_soon'] == '1': 
	<font color="#f00000"><b>このスレは古いので、もうすぐ消えます。</b></font><br>
% endif


<table border=0>
	% for reslog in log['res']:
	<tr>
		<td nowrap align="right" valign="top">…</td>
		<td bgcolor="#F0E0D6" nowrap>
			<input type="checkbox" name="${reslog['no']}" value="delete">
			<font color="#cc1105" size=+1><b>${reslog['sub']}</b></font>
			Name <font color="#117743"><b>${(reslog['name'], reslog['email']) | fil.email_link, n}</b></font> 
			${reslog['now']} No.${reslog['no']} &nbsp;
			${reslog['pict'] | n}<blockquote>${reslog['com'] | fil.auto_link, fil.comment_fix, n}</blockquote>
		</td>
	</tr>
	% endfor
</table>
<br clear=left><hr>
% endfor
<table align=right>
	<tr>
		<td nowrap align=center>
			<input type=hidden name=mode value=usrdel>
			【記事削除】[
			<input type=checkbox name=onlyimgdel value=on>画像だけ消す]<br>
			削除キー
			<input type=password name=pwd size=8 maxlength=8 value="">
			<input type=submit value="削除">
		</td>
	</tr>
</table>
</form>
% if res == 0:
	<table align=left border=0 bgcolor="#ff8080"><tr>
		<form action="/${conf.SELF_NAME}/${page - 1}" method="post">
			<td>
	% if page == 0:
			前のページ
	% else:
			<input type=submit value="前のページ">
	% endif
			</td>
		</form>
			<td>
	% for p in range((count // conf.PAGE_DEF) + 1):
		% if page == p:
			${p}&nbsp;
		% else:
			<a href="/${conf.SELF_NAME}/${p}">${p}</a>&nbsp;
		% endif
	% endfor
			</td>
		<form action="/${conf.SELF_NAME}/${page + 1}" method="post">
			<td>
	% if page == count // conf.PAGE_DEF:
			次のページ
	% else:
			<input type=submit value="次のページ">
	% endif
			</td>
		</form>
	</tr></table><br clear=all>
% endif
<%include file="footer.mak"/>
