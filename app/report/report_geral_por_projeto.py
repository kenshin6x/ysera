#!python
# -*- coding: utf-8 -*-

from ..core import redmine_ticket_report

__version__ = "1"
__author__ = "Junior Andrade"
__email__ = "seisxis@gmail.com"

from redmine_ticket_report import RedmineTicketReport


class ReportGeralPorProjeto(RedmineTicketReport):
    def __init__(self):
        self.subject = "Relatório de Tickets - Geral Por Projeto"
        self.query = """ 
            select
                x.projeto,
                x.total as "total de chamados",
                round((x.total::numeric * 100 / sum(x.total) over ()), 2) || '%' as "% sobre todos os chamados",
                x.resolvidos,
                x."% resolvidos",
                x.pendentes,
                x."% pendentes",
                x.pendentes_cliente as "pendentes pelo cliente",
                x."% pendentes pelo cliente",
                x.pendentes_tecnotech as "pendentes pela tecnotech",
                x."% pendentes pela tecnotech"
                --round((x.resolvidos::numeric * 100 / sum(x.resolvidos) over ()), 2) || '%' as "% geral resolvidos",
                --round((x.pendentes::numeric * 100 / sum(x.pendentes) over ()), 2) || '%' as "% geral abertos"
                from (
                select
                    *,
                    case when x.total > 0 then round((x.resolvidos::numeric * 100 / x.total), 2) || '%' else '0' end as "% resolvidos",
                    case when x.total > 0 then  round((x.pendentes::numeric * 100 / x.total), 2) || '%' else '0' end as "% pendentes",
                    case when x.pendentes > 0 then  round((x.pendentes_cliente::numeric * 100 / x.pendentes), 2) || '%' else '0' end as"% pendentes pelo cliente",
                    case when x.pendentes > 0 then  round((x.pendentes_tecnotech::numeric * 100 / x.pendentes), 2) || '%' else '0' end as "% pendentes pela tecnotech"
                from (
                    select
                    p.name as projeto,
                    (select count(distinct i.id) from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id) as total,
                    (select count(distinct i.id) from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id and si.is_closed is true) as resolvidos,
                    --(select extract(epoch from avg(age(i.closed_on, i.created_on)) / 86400)::int from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id and si.is_closed is true) as resolvidos_espera_dias,
                    (select count(distinct i.id) from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id and si.is_closed is false) as pendentes,
                    (select count(distinct i.id) from issues as i
                    inner join users as u on u.id = i.assigned_to_id
                    inner join members as m on m.project_id = p.id and m.user_id = u.id
                    inner join issue_statuses as si on si.id = i.status_id
                    where
                        i.project_id = p.id
                        and si.is_closed is false
                        and exists (
                                select 1 from member_roles as mr
                                inner join roles as r on r.id = mr.role_id
                                where
                                        mr.member_id = m.id
                                        and (r.name ilike '%crea%' or r.name ilike '%cft%')
                        )
                    ) as pendentes_cliente,
                    (select count(*) from issues as i
                    left join users as u on u.id = i.assigned_to_id
                    left join members as m on m.project_id = p.id and m.user_id = u.id
                    inner join issue_statuses as si on si.id = i.status_id
                    where
                        i.project_id = p.id
                        and si.is_closed is false
                        and (exists (
                                select 1 from member_roles as mr
                                inner join roles as r on r.id = mr.role_id
                                where
                                        mr.member_id = m.id
                                        and r.name ilike '%tecnotech%'
                        )
                        )
                    ) as pendentes_tecnotech
                    from projects as p
                    where
                        (p.name ilike '%sitac - crea%' or p.name ilike '%sinceti - cft%')
                    order by total desc, p.name asc
                ) as x
            ) as x
        """

        super().__init__()


if __name__ == '__main__':
    o = ReportGeralPorProjeto()
