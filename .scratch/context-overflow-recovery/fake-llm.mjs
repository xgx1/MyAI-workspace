// Minimal DeepSeek Messages (Anthropic wire) fake for the overflow-recovery A/B.
// Mode file: /tmp/fake-llm.mode holds "1" meaning "fail the next conversation
// request with the real 400 envelope"; the server rewrites it to "0" when it does.
import http from 'node:http'
import fs from 'node:fs'

const MODE = '/tmp/fake-llm.mode'
const LOG = '/tmp/fake-llm.log'
const OVERFLOW = "This model's maximum context length is 1048576 tokens. "
  + 'However, you requested 1098368 tokens (705152 in the messages, 393216 in the completion). '
  + 'Please reduce the length of the messages or completion.'
const PORT = 18999
let requests = 0

function note(line) {
  fs.appendFileSync(LOG, `${new Date().toISOString()} ${line}\n`)
}

function sse(res, text) {
  res.writeHead(200, {
    'content-type': 'text/event-stream',
    'cache-control': 'no-cache',
    connection: 'keep-alive',
  })
  const send = (payload) => res.write(`data: ${JSON.stringify(payload)}\n\n`)
  send({
    type: 'message_start',
    message: {
      id: 'msg_fake',
      type: 'message',
      role: 'assistant',
      model: 'deepseek-flash',
      content: [],
      stop_reason: null,
      stop_sequence: null,
      usage: { input_tokens: 10, output_tokens: 1 },
    },
  })
  send({ type: 'content_block_start', index: 0, content_block: { type: 'text', text: '' } })
  send({ type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text } })
  send({ type: 'content_block_stop', index: 0 })
  send({
    type: 'message_delta',
    delta: { stop_reason: 'end_turn', stop_sequence: null },
    usage: { output_tokens: 5 },
  })
  send({ type: 'message_stop' })
  res.end()
}

const server = http.createServer((req, res) => {
  let body = ''
  req.on('data', (chunk) => { body += chunk })
  req.on('end', () => {
    requests += 1
    if (!req.url.includes('/v1/messages')) {
      note(`#${requests} ${req.method} ${req.url} -> 404`)
      res.writeHead(404, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ type: 'error', error: { type: 'not_found_error', message: 'fake: unknown path' } }))
      return
    }
    let parsed
    try {
      parsed = JSON.parse(body)
    } catch (error) {
      note(`#${requests} bad json: ${error.message}`)
      res.writeHead(400, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ type: 'error', error: { type: 'invalid_request_error', message: 'fake: bad json' } }))
      return
    }
    const messages = Array.isArray(parsed.messages) ? parsed.messages : []
    const lastText = (() => {
      for (let i = messages.length - 1; i >= 0; i -= 1) {
        const content = messages[i].content
        if (typeof content === 'string') return content
        if (Array.isArray(content)) {
          const joined = content.map((block) => (block && block.type === 'text' ? block.text : '')).join('')
          if (joined.length > 0) return joined
        }
      }
      return ''
    })()
    const summary = lastText.includes('acting as a compaction engine')
    const mode = fs.existsSync(MODE) ? fs.readFileSync(MODE, 'utf8').trim() : '0'
    if (!summary && mode === '1') {
      fs.writeFileSync(MODE, '0')
      note(`#${requests} conversation msgs=${messages.length} -> 400 overflow (mode consumed)`)
      res.writeHead(400, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ type: 'error', error: { type: 'invalid_request_error', message: OVERFLOW } }))
      return
    }
    note(`#${requests} ${summary ? 'SUMMARY' : 'conversation'} msgs=${messages.length} -> 200`)
    sse(res, summary ? '## Primary Request and Intent\n- fake checkpoint' : 'OK')
  })
})

server.listen(PORT, '127.0.0.1', () => note(`listening on 127.0.0.1:${PORT}`))
