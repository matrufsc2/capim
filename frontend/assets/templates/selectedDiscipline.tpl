<td title="<%- discipline.get('_title') || discipline.get('name') %>" class="has-tip" data-tooltip><%- discipline.get("code") %></td>
<td><%- discipline.team ? discipline.team.get("code") : (!discipline.teams.isSynced() ? "Carregando..." : "-")  %></td>
<td><%- discipline.semester ? discipline.semester.get("name") : '-' %></td>
<td><a href='#'><i class="icon-up"></i></a></td>
<td><a href='#'><i class="icon-down"></i></a></td>
<td><a href='#'><i class="icon-delete"></i></a></td>