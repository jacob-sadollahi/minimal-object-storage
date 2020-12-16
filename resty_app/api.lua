local http = require("socket.http")
local ltn12 = require("ltn12")
local AWS = require('lua-aws.init')

local s3_error_messages = {["409"] = "BucketAlreadyExists", ["400"] = "TooManyBuckets", ["422"] = "InvalidArgumentsInName"}


function sendRequest(path, payload, method, auth_header)
    local path = path
    local payload = payload
    local response_body = {}
    local local_source = nil
    if method == "POST" then
        local_source = ltn12.source.string(payload)
    end

    local res, code, response_headers, status = http.request
        {
            url = path,
            method = method,
            headers =
            {
                ["Authorization"] = auth_header,
                ["Content-Type"] = "application/json",
                ["Content-Length"] = payload:len()
            },
            source = local_source,
            sink = ltn12.sink.table(response_body)
        }
    return table.concat(response_body), code, status
end

function strSplit(delim, str)
    local t = {}

    for substr in string.gmatch(str, "[^" .. delim .. "]*") do
        if substr ~= nil and string.len(substr) > 0 then
            table.insert(t, substr)
        end
    end

    return t
end

function createBucket(bucket_name)
    local aws = AWS.new({
        accessKeyId = os.getenv('S3_ACCESS_KEY'),
        secretAccessKey = os.getenv('S3_SECRET_KEY'),
        preferred_engines = "curl",
        region = os.getenv('S3_REGION'),
        endpoint = os.getenv('S3_ENDPOINT'),
    })
    local ok, r
    ok, r = aws.S3:api():createBucket({ Bucket = bucket_name })
    --    if not ok then error(r) end
    return r, ok
end

ngx.req.read_body();
local cjson = require("cjson")
local reqPath = ngx.var.uri:gsub("resty%-api/", "");
local reqMethod = ngx.var.request_method
local body = ngx.req.get_body_data() ==
        nil and {} or cjson.decode(ngx.req.get_body_data());
local headers = ngx.req.get_headers()

Api = {}
Api.__index = Api
Api.responded = false;
function Api.endpoint(method, path, callback)
    if Api.responded == false then
        local final_data = {}
        local parsed_data = {}
        local res = ""
        local code = ""
        local status = ""
        if string.find(path, "<(.-)>") then
            local splitPath = strSplit("/", path)
            local splitReqPath = strSplit("/", reqPath)
            for i, k in pairs(splitPath) do
                if string.find(k, "<(.-)>") then
                    parsed_data[string.match(k, "%<(%a+)%>")] = splitReqPath[i]
                    reqPath = string.gsub(reqPath, splitReqPath[i], k)
                end
            end
            res, code, status = sendRequest("http://middleware:5000/middleware/api/v1/storage/bucket/check/" .. parsed_data["name"],
                "",
                "GET",
                headers['Authorization'])
            if code ~= 200 then
                return ngx.say(cjson.encode({
                    error = code,
                    message = cjson.decode(res)["msg"]
                }))
            elseif code == 200 then
                local bucket_res, bucket_ok
                bucket_res, bucket_ok = createBucket(parsed_data["name"])
                if bucket_ok ~= true then
                    return ngx.say(cjson.encode({
                        error = bucket_res["code"],
                        message = s3_error_messages[tostring(bucket_res["code"])]
                    }))
                end
                final_data["result"] = "created"
                final_data["status"] = "200"
            end
        end

        if reqPath ~= path then
            return false;
        end
        if reqMethod ~= method then
            return ngx.say(cjson.encode({
                error = 400,
                message = "Method " .. reqMethod .. " not allowed"
            }))
        end

        Api.responded = true;

        body.data = final_data
        return callback(body);
    end

    return false;
end

Api.endpoint('GET', '/bucket/<name>',
    function(body)
        return ngx.say(cjson.encode({
            method = method,
            path = path,
            body = body,
        }));
    end)